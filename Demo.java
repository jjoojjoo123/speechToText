/* Copyright 2008, 2009, 2010 by the Oxford University Computing Laboratory

   This file is part of HermiT.

   HermiT is free software: you can redistribute it and/or modify
   it under the terms of the GNU Lesser General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   HermiT is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU Lesser General Public License for more details.

   You should have received a copy of the GNU Lesser General Public License
   along with HermiT.  If not, see <http://www.gnu.org/licenses/>.
*/


import org.semanticweb.HermiT.Reasoner;
import org.semanticweb.HermiT.EntailmentChecker;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.reasoner.InferenceType;

import java.io.File;
import java.io.PrintWriter;
import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.FileNotFoundException;
import java.io.IOException;

import java.util.HashSet;
import java.util.Set;

import static java.lang.System.out;

/**
 * This example demonstrates how HermiT can be used to check the consistency of the Pizza ontology
 */
public class Demo {

    private static OWLOntologyManager m;

    public static void main(String[] args) throws Exception {
        if(args.length == 0){
            out.println("Please enter one command.");
            return;
        }
        if(args.length == 1){
            out.println("Please enter one owl file.");
            return;
        }
        // First, we create an OWLOntologyManager object. The manager will load and save ontologies.
        m=OWLManager.createOWLOntologyManager();
        switch(args[0]){
            case "cons":{
                out.println(consistent(args[1]));
                break;
            }
            case "c":{
                if(args.length < 3){
                    out.println("Please enter one owl file to output, or '-' to stdout.");
                    break;
                }
                classify(args[1], args[2]);
                break;
            }
            case "e":{
                if(args.length < 3){
                    out.println("Please enter one conclusion owl file.");
                    break;
                }
                out.println(entailment(args[1], args[2]));
                break;
            }
            default:{
                out.println("Unknown command.");
            }
        }
    }
    private static Reasoner buildReasoner(String path) throws Exception {
        // We use the OWL API to load the Pizza ontology.
        OWLOntology o=m.loadOntologyFromOntologyDocument(new File(path));
        // Now, we instantiate HermiT by creating an instance of the Reasoner class in the package org.semanticweb.HermiT.
        return new Reasoner(o);
    }
    public static boolean consistent(String path) throws Exception {
        return buildReasoner(path).isConsistent();
    }
    public static void classify(String infile, String outfile) throws Exception {
        PrintWriter output;
        Reasoner hermit = buildReasoner(infile);
        if(outfile == "-"){
            output = new PrintWriter(System.out);
        }else{
            // code from HermiT CommandLine.java
            try {
                File file=new File(outfile);
                if (!file.exists())
                    file.createNewFile();
                file=file.getAbsoluteFile();
                output=new PrintWriter(new BufferedOutputStream(new FileOutputStream(file)),true);
            }
            catch (FileNotFoundException e) {
                throw new IllegalArgumentException("unable to open "+outfile+" for writing");
            }
            catch (SecurityException e) {
                throw new IllegalArgumentException("unable to write to "+outfile);
            }
            catch (IOException e) {
                throw new IllegalArgumentException("unable to write to "+outfile+": "+e.getMessage());
            }
        }
        Set<InferenceType> inferences=new HashSet<InferenceType>();
        inferences.add(InferenceType.CLASS_HIERARCHY);
        inferences.add(InferenceType.OBJECT_PROPERTY_HIERARCHY);
        //inferences.add(InferenceType.DATA_PROPERTY_HIERARCHY);
        hermit.precomputeInferences(inferences.toArray(new InferenceType[0]));
        hermit.dumpHierarchies(output, true, true, false);
        output.flush();
    }
    public static boolean entailment(String p, String c) throws Exception {
        Reasoner hermit=buildReasoner(p);
        OWLOntology conclusion=m.loadOntologyFromOntologyDocument(new File(c));
        EntailmentChecker checker=new EntailmentChecker(hermit, m.getOWLDataFactory());
        return checker.entails(conclusion.getLogicalAxioms());
    }
}