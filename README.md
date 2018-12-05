# speechToText
資管專題

## Python version
Python 3.7+ is required because subprocess.run receives capture_output parameter.

## SWI-Prolog
Install the newest version is OK.

## Python虛擬環境
### 安裝virtualenv
pip install virtualenv

### 架構virtualenv
cd 目標資料夾

virtualenv 子資料夾名稱

將創一個子資料夾作為虛擬環境

### 切換虛擬環境
(Linux)那個子資料夾/bin/activate

(Windows)那個子資料夾\Scripts\activate

(Set-ExecutionPolicy RemoteSigned)

### 模組
#### Flask
pip install Flask
#### numpy
pip install numpy

or install by wheel: https://www.lfd.uci.edu/~gohlke/pythonlibs/
#### networkx (optional, one of networkx and pyswip is needed)
pip install networkx
#### pyswip (optional, one of networkx and pyswip is needed)
套件本身需要SWI-Prolog的環境才能安裝

由於之前已經載明了需要SWI-Prolog的環境，所以這個條件應是自動滿足。

pip install pyswip