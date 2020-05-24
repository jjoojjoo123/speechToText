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
(Linux)source 那個子資料夾/bin/activate

(Windows)那個子資料夾\Scripts\activate

(Set-ExecutionPolicy RemoteSigned)

### 模組
#### Flask
pip install Flask

*import flask*
#### numpy
pip install numpy

or install by wheel: https://www.lfd.uci.edu/~gohlke/pythonlibs/
#### SpeechRecognition
pip install SpeechRecognition

*import speech_recognition*
#### networkx (optional, one of networkx and pyswip is needed)
pip install networkx
#### pyswip (optional, one of networkx and pyswip is needed)
套件本身需要SWI-Prolog的環境才能安裝

由於之前已經載明了需要SWI-Prolog的環境，所以這個條件應是自動滿足。

pip install pyswip

#### pynput, pyaudio (optional)
speechToText.py當中使用的
定義了一套在命令行使用的API
網頁app沒有調用
裡頭的功能由web_recognize.py取代

基本上web_recognize.py與speechToText.py這兩個檔案的東西都可以再模組化

### 額外檔案
#### API_keys.py (設定使用語音辨識API所需要的key)
內容大概長這樣
```Python
import globalvar as gl

gl._init()

gl.set_value("ibm_username" ,"...")
gl.set_value("ibm_password", "...")
gl.set_value("wit_key", "...")
gl.set_value("houndify_id", "...")
gl.set_value("houndify_key", "...")
```

### 一些API解說
因為寫這段時已經過了一年半載，所以沒辦法寫得太詳細

#### string_align.py
整個project的一大核心，定義了有關字串之間相似度的演算法

##### `class Param`
把後續所有演算法用到的參數全都塞到同一個類別
其實應該要讓每一個演算法用到的參數分開來放

##### `class StringAlign`
演算法的主要工作地點
裡頭存放著若干字串等待計算

###### `self.push(*args: Union[str, List[str]])`
把要算的字串，或者是list of 字串，丟到物件裡頭等待計算
所有字串在丟進去時會經過前處理

###### `self.push_list(l: List[str])`
道理同上，丟的是list of 字串

###### `self.concat(n: StringAlign)`
道理同上，把另外一個`StringAlign`物件裡頭存放的字串全都塞進來

###### `self.__iadd__(n: Union[List[str], StringAlign])`
道理同上，`+=`運算子右方可放list of 字串或`StringAlign`物件

###### `self.sentences(n: Union[List[str], StringAlign])`
道理同上，`+=`運算子右方可放list of 字串或`StringAlign`物件

###### `self.evaluate(param: Param)`
依照param的參數執行演算法，計算字串兩兩之間的相似度
並在計算結束後更新`self._state`
此演算法接收以下參數：
`param.use_stem: bool` 會不會讓字串做stemming前處理
`param.lowercast: bool` 會不會讓字串做小寫化前處理
`param.init_value: ScoreType` 算分演算法的基礎分數（最低分）
`param.base_point: Callable[[List[str], List[str]], ScoreType]` 當兩個字串沒有共通的詞彙時要當成幾分

`param.merge_point: Callable[[Tuple[List[str], List[str]], Tuple[List[str], List[str]], Ans, Ans], ScoreType]`
其中`Ans`相當於`Tuple[ScoreType, List[AnchorType]]`
其中`AnchorType`物件可以當成一個2-tuple `(a, b)`，代表對於字串s1與s2有`s1[a] == s2[b]`

演算法執行的過程是：
1. 將`StringAlign`物件當中存放的字串進行前處理，並把字串打成list of words（List[str]）
2. 把某兩個字串，稱為s1與s2，丟進去計算分數
3. 計算分數前先找出所有的anchor，代表我們找出所有s1與s2的共通詞彙
4. 挑出其中一個anchor，從這個anchor將兩個字串分成左右半邊
5. 把兩個左半邊的字串丟進去算分，兩個右半邊以此類推
6. 如果兩個字串沒有共通詞彙（Base case），呼叫`param.base_point`計算此時應該給幾分
7. 算完左右半邊的分數後，統整左右半邊計算過程中分數最高的anchors
8. 呼叫`param.merge_point`
這個函數有四個參數：兩個左半邊字串（包成Tuple）、兩個右半邊字串、左半邊算出的結果與右半邊算出的結果
輸出一個分數
9. 將7.得到的anchors加上現在使用的anchor，並與6.或8.算出的分數回傳（封裝成`Ans`物件）
10. 算出以所有anchors作為起始點的分數之後，找出最高者，回傳最高者的`Ans`物件

實作當中這是一個兩函數遞迴，一個固定單一anchor計算分數，一個負責從所有anchors當中找尋最大分數

###### `self._state: StringAlign.State`
`state.length`代表目前已計算完分數的字串有多少個
由於物件當中的字串只增不減，所以就相當於在存入幾個字串時觸發過運算
`state.Dict[a, b]` 代表第a與第b字串的計算結果（`Ans`物件）

###### `self.__str__()`
如果觸發過`evaluate`會將計算結果顯示出來

###### `self.big_anchor_concat_heuristic(param: Param, confidence: Optional[List[T]])`
依照param的參數執行演算法，計算每個字串之間哪些詞彙的定位是相同的
比如說"A apple"與"B apple"兩個句子當中的'apple'就很有可能被認定為是兩個字串當中「相同定位」的詞彙
相同定位的詞彙一定要是同樣的詞彙，並且在句子中出現的位置有一定程度的相似性

此演算法會用到param的參數：
`param.base_confidence: T` 如果沒有指定某個字串的可信度，則以此值代替
`param.score_map: Callable[[List[T], State], Dict[Tuple[int, int], ScoreType]]`
我們前面算過兩個字串之間的相似度
這個函數則是將我們算出來的分數與兩個字串個別的可信度進行計算，得到這兩個字串的調整後分數
實作上有關confidence的調整並沒有使用，因為好麻煩，而且在後面`self.final_result()`就有相似且直觀的機能可以使用了
但這機制依然保留著以便改寫

總之回來講`big_anchor_concat_heuristic`在做什麼
這名字就已經講述了這函數大略要做的事情
就是把之前算出的，兩個字串彼此之間的小anchor，變成所有字串共享的大anchor
且演算法本身概念相當直覺（經過之前`evaluate`的荼毒，你一定會覺得現在這個很簡單）

我們有一個`dict`，key是諸如`(0, 1)`這樣的pair，value則是這兩個字串彼此的相似度
這演算法先從分數最高的字串對s1 s2（也就是最相似的兩個字串）
把之前計算時，使它們分數最大化的anchors抓出來
假設`anchors = [(0, 0), (1, 1), (2, 3)]`
那麼我們將s1的0號詞與s2的0號詞「視為相同定位」、s1的1號詞與s2的1號詞、s1的2號詞與s2的3號詞等
以此類推
最後做上標記，代表s1與s2已經「是同一國」的了
接著找第二相似的字串對重複以上動作
若兩個字串已經是同一國則直接跳過，因為之前就有分數更高的解決方案

上面的「相同定位」與「同一國」都是equivalent relation
其中一個性質是有1與2、2與3，就有1與3
內部實現是使用**disjoint set**這種資料結構

最後直接回傳所有「相同定位」的資訊
這個資訊是一個只有一個key的`dict`，key叫做`"word_set"`
未來若有其他演算法，也可以擴充其他key來使用，但至少要有這個資訊以便輸出最終結果

###### `self.big_anchor_concat_james(param: Param)`
另外一個做大anchor的函數

此演算法接收以下參數：
`param.use_stem: bool` 會不會讓字串做stemming前處理
`param.lowercast: bool` 會不會讓字串做小寫化前處理

其餘程序我看不懂，app終端也沒有呼叫這個函式
因為它實在太大了

###### `self.give_graph()`
做完大anchor後，將所有定位群集描繪成圖形並找出彼此的前後關係
這函數會自動被後面兩個函式呼叫

由於單一字串內的前後關係是確定的，所以會一一看每個字串
將每個詞彙代表的定位做成一個node，並連到下一個詞彙代表的定位
這樣子每個字串都做過一次後，就會得到一個graph
下面兩個函式基本上都會對這個graph進行topological sort以找出每個定位的前後關係

注意這個地方與下方兩個函式都會用同一個模組進行圖像處理
個人推薦使用networkx處理這件事
使用pyswip可以用邏輯的方法找出前後關係，只是我說真的很難看得懂，好graph不用嗎

###### `self.str_big_anchor()`
將做完大anchor的結果輸出成直觀的圖像化字串
真的會把所有相同定位的詞彙垂直對齊在一起
用了就知道視覺效果如何

要注意的是因為不是所有字串都有某一個定位的詞彙
所以有些定位之間的關係可能會錯落不致
因為它們在拓蹼學上沒有前後關連

###### `self.final_result(weight: List[T], threshold: List[T])`
做完大anchor之後將這些字串合併成單一句子
給定每個句子對應的權重（票數）以及門檻值
某個定位出現在某個句子則拿到這個句子的票數
若這個定位的得票過了門檻值則會被收進句子裡
再依照這些定位的拓蹼學順序由左到右

##### give_param(way) -> Param
`way` is one of `"wayne"` or `"james"`
這函數輸出`Param`物件
儘管物件有很多參數可以調整，但這函數是為了`StringAlign.evaluate`設計的，所以只會有三個參數

這邊來介紹兩種方法的差異

###### "wayne" way
兩個字串的相似度介於0到1之間

若兩個字串沒有共通詞，分數是`1 / (len(s1) + len(s2) + 1)`
這邊的字串都是list of 詞彙，所以`len`取出來的結果是詞彙數量而非字元數量
若兩字串都為空，很自然地這兩個字串會是「相同」的，當然應該要有最高的相似度
其餘狀況則是依照詞彙數量而衰減
這邊是採用最簡單的衰減函式

在算完左右半字串的相似度之後
將字串分成三部分：左半、anchor自己（s1的一個詞與s2的一個詞）與右半
左半與右半的相似度是已經得出來的
s1的anchor與s2的anchor因為都是同一個詞組成的字串，相似度當然是1
將這三部分的相似度依照總詞數（s1部分的詞彙數+s2部分的詞彙數）進行加權平均

比如
s1 = A B 'C' D E
s2 = B 'C' D E F
那麼左半的詞彙數：3，anchor自己的詞彙數：2（定質），右半的詞彙數：5
假設左半的分數為x，右半為y
則計算結果為`(3x + 2 + 5y) / (3 + 2 + 5)`
計算的結果也會落在0到1之間
且對於左右半完全相符的字串計算結果會是1

###### "james" way
兩個字串的相似度介於正負len(s1) + len(s2)之間

若兩個字串沒有共通詞，分數是`-(len(s1) + len(s2))`
若兩字串都為空，相似度為0，因為沒有共通詞而造成的懲罰程度最輕
其餘狀況則依照詞彙總數而衰減

在算完左右半字串的相似度後
將左邊的分數與右邊的分數加總，並加上代表anchor自己的2

比如
s1 = A B 'C' D E
s2 = B 'C' D E F
假設左半的分數為x，右半為y
則計算結果為`x + 2 + y`

#### final_result.py
定義`to_final_result`，是上述所有程序的包裝，直接被app調用

#### web_recognize.py
定義`recognize`函數直接被app調用

#### speechToText.py
**需要額外模組（前述）**
定義一套在指令行使用的錄音辨識程式，沒有被網頁端app調用
但核心機能與web_recognize.py有所重疊
需要模組化

#### disjoint_set.py
定義disjoint set這種資料結構

#### use_reasoner.py
也沒有被網頁app調用
這是一個用shell把python與JAVA的reasoner接上的小程式
不過因為前面算出的單一字串不見得能符合ACE文法，所以這端也就沒接上了
只能用來呈現「如果有的話應該會是什麼樣」

### 後記
以後再補充
果然不該在一年半後才回來寫細節，細節都忘得差不多了