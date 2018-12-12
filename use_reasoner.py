import os
import re
import subprocess
import platform

URI = 'http://attempto.ifi.uzh.ch/ontologies/owlswrl/test'
reasoner = 'HermiT.jar'
ape = 'ape'
owl_to_ace = 'owl_to_ace'
demo_class = 'Demo'

debug = True

ape_command = lambda filename: [ape, '-file', filename, '-solo', 'owlxml']
owl_to_ace_command = lambda filename: [owl_to_ace, '-xml', filename]

plat = platform.system()
exe_tail = '.exe' if plat == 'Windows' else ''

if not os.path.exists(reasoner):
	print("Cannot find reasoner.")

if not os.path.exists(f'{ape}{exe_tail}'):
	print("Cannot find ape")

if not os.path.exists(f'{owl_to_ace}{exe_tail}'):
	print("Cannot find owl_to_ace")

if not os.path.exists(f'{demo_class}.class'):
	subprocess.run(
		['javac',
		 '-cp',
		 reasoner,
		 f'{demo_class}.java'], shell = True)

def run(storypath, querypath):
	with open(f'{storypath}.owl', 'wb') as file:
		s = subprocess.run(ape_command(filename = storypath), capture_output = True)
		file.write(s.stdout)
	with open(f'{querypath}.owl', 'wb') as file:
		q = subprocess.run(ape_command(filename = querypath), capture_output = True)
		file.write(re.sub(b'ontologyIRI=".*"', b'ontologyIRI=""', q.stdout))
	result = subprocess.run(
		['java',
		 '-cp',
		 f'''.{';' if plat == 'Windows' else ':'}{reasoner}''',
		 demo_class,
		 'e',
		 os.path.abspath(f'{storypath}.owl'),
		 os.path.abspath(f'{querypath}.owl')], capture_output = True, shell = (True if plat == 'Windows' else False))
	#print(result.stdout)
	if not debug:
		os.remove(f'{storypath}.owl')
		os.remove(f'{querypath}.owl')
	if b'true' in result.stdout:
		return 'True'
	elif b'false' in result.stdout:
		return 'False'
	else:
		return result.stdout.decode()