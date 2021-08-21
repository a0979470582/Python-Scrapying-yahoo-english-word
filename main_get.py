import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import re
import json

#加入索引增加搜尋速度: db.allWordHtml.createIndex({wordName:1})
client = MongoClient("mongodb://localhost:27017/")
database = client['yahooData']
collection = database['allHtml']

file_name_list = os.listdir("book/book")#所有的單字檔案名稱

#輸出不重複的單字列表
def output_no_repeat_file():

    all_list = []
    for file_name in file_name_list:
        
        if not file_name.endswith(".txt"):
            continue #避免資料夾內包含紀錄檔等非.txt檔案
            
        with open("book/book/"+file_name, 'rt') as file:
            word_list = file.readlines()
            for word in word_list:
                if word not in all_list:
                    all_list.append(word)
            print(len(all_list))

    text = ""
    with open("book/"+"no_repeat.txt", 'wt') as file:
        for a in all_list:
            text += a
        file.write(text)
        
#排序不重複單字列表
def sort_word():
    with open("book/no_repeat.txt", "rt") as file:
        word_list = file.readlines()
        new_list = []
        new_text = ""
        for word in word_list:
            
            #列表為空直接放入
            if len(new_list) == 0:
                new_list.append(word)
                continue

            #由小至大排序單字, A=41, a=61
            position = 0
            for new_word in new_list:
                if word > new_word:
                    position += 1
            new_list.insert(position, word)  

        #轉為純文字
        for word in new_list:
            new_text += word
            
        with open("book/no_repeat2.txt", "wt") as file:
            file.write(new_text)
        
#檢查wordName是否為空
def checkMyData():
    c = 0
    for row in loadAll():
        c = c+1
        html = row['html']
        wordNameInHtml = getWordNameInHtml(html)
        if wordNameInHtml == None:
            print("None")
        elif wordNameInHtml == "":
            print("空字串")
        if(c % 100 == 0):
            print(c)    
                
#輸出至紀錄檔
def logCrawlProgress(info):
    with open('GetWord.log','at') as file:
        time_string = datetime.now().strftime('%H:%M:%S')
        file.write(info+" "+time_string+"\n")

def loadAll():
    return collection.find({})

def loadAllCount():
    return collection.find({}).count()

#多個搜尋關鍵字可能會指向同一個單字, 所以兩者都要記錄
def loadHtml(wordName):
    return collection.find({'$or':[{'wordName':{'$eq':word.strip('\n')}}, {'wordNameQuery':{'$eq':word.strip('\n')}}]})

def insertHtml(wordNameQuery, wordName, html):
    collection.insert_one({"wordNameQuery":wordNameQuery, "wordName":wordName, "html":html})

def isExistsHtml(wordName):
    return False if loadHtml(wordName).count() == 0 else True

#從yahoo字典取得html
def getHtml(wordName):
    url = "https://tw.dictionary.search.yahoo.com/search?p="+wordName
    html = requests.get(url).text
    return html

#從html中取得wordName
def getWordNameInHtml(html):
    bs = BeautifulSoup(html, 'html.parser')
    wordNameTag = bs.find("span", {'class':"fz-24 fw-500 c-black lh-24"})
    return "" if(wordNameTag == None) else wordNameTag.text
    
#傳入html, 解析後返回單字(dict)
def analyze_html(html):
    bs = BeautifulSoup(html, 'html.parser')

    #若無單字卡元素表示連線失敗(被封鎖或無此單字)
    card_element = bs.find('div', {'class':'dictionaryWordCard'})
    if card_element == None :
        return None
    
    #單字名稱
    word_name = card_element.select('h3.title span.fz-24')[0].text
    
    #音標
    pronunciation = card_element.select("li.d-ib span")[0].text.replace(
        "KK", "").replace("[", "/ ").replace("]", " /") if len(card_element.select("li.d-ib span")) > 0 else ""

    #解釋
    translation = ""
    for li_element in card_element.select("div.dictionaryWordCard div.compList.p-rel li"):
        
        one_line = ""
        for div_element in li_element.select("div"):
            one_line += div_element.text+" "
            
        one_line = one_line.replace("；", "。").replace("（", "(").replace("）", ")")
        translation += one_line+"\n"
        
    translation = translation.strip('\n')
    
    #三態變化區域
    b_html = ""
    for span_element in card_element.select("li.ov-a span"):
        b_html += span_element.decode_contents()

    #三態變化
    variation = ""
    for b_element in b_html.split('</b>'):
        variation += b_element.strip()+"\n"
    variation = variation.replace("<b>", "").strip('\n')
    
    
    #例句
    example = ""
    
    example_element = bs.find('div', {'class':"grp-tab-content-explanation"})
    if example_element!=None and len(example_element) != 0:
        
        part_of_speech_list = [] #['vt.及物動詞', 'n.名詞']
        for div in example_element.select("div.compTitle"):
            one_line = ""
            for span in div.select('span'):
                one_line += span.text

            part_of_speech_list.append(one_line)

        block_list = []
        for div in example_element.select("div.grp-tab-content-explanation div.compTextList"):
            many_line = ""
            for li in div.select('li'):
                one_line = ""
                one_line += li.select("span.fw-xl")[0].text+" "
                one_line += li.select("span.d-i")[0].text
                for span in li.select("span.fc-2nd"):
                    one_line += ("\n" + span.text)
                one_line += "\n"
                many_line += one_line+"\n"


            block_list.append(many_line)


        for index, speech in enumerate(part_of_speech_list):
            example += (speech + '\n' + block_list[index])
        example = example.strip('\n')  
    
    #正反義詞
    synonyms_element = bs.select("div.grp-tab-content-synonyms")
    
    synonyms = ""
    if len(synonyms_element) != 0:     
        for children in synonyms_element[0].children:
            one_line = ""
            if 'compDlink' in children.attrs['class']:
                for li in children.select('li'):
                    one_line += li.text
                one_line += '\n'
            else:
                one_line = children.select('span')[0].text

            synonyms += one_line+'\n'
        synonyms = synonyms.strip('\n')    
    
    #音檔連結
    audio_url = ""
    audio_name = word_name.strip(' ').replace(' ', '_')
    result = re.findall("https:.{10,100}"+audio_name+".{0,15}\.mp3", str(bs.html), re.IGNORECASE)
    if len(result) > 0:
        audio_url = result[0].replace("\\", "")
    
    if audio_url == "":
        logCrawlProgress("no music "+ word_name)
    
    return {
        'word_name': word_name,
        'pronunciation': pronunciation,
        'translation': translation,
        'variation': variation,
        'example': example,
        'synonyms': synonyms,
        'audio_url': audio_url
    }

#給予單字, 從yahoo取得html並存入DB
def main_get(wordNameQuery=""):
    if wordNameQuery == "":
        return
    
    html = getHtml(wordNameQuery)#yahoo
      
    wordName = getWordNameInHtml(html)
        
    #有時連線失敗無法取得單字, 紀錄下來
    if wordName == None:
        logCrawlProgress(wordNameQuery+" None from yahoo")
        return
    if wordName == "":
        logCrawlProgress(wordNameQuery+" Empty from yahoo")
        return
        
    collection.insert_one({"wordNameQuery":wordNameQuery, "wordName":wordName, "html":html})
    logCrawlProgress(wordNameQuery+" 插入成功")    

#走訪no_repeat內的單字, 從yahoo取得html後存入DB
def start_main_get():
    with open("book/"+"no_repeat.txt", "rt") as file:
        for word in file.readlines():
            main_getWordAndSave(word.strip('\n'))

#將個別檔案的單字解析後, 輸出json
def output_json_book():
    file_name_list = [
        '高中分級level1.txt',
        '高中分級level2.txt',
        '高中分級level3.txt',
        '高中分級level4.txt',
        '高中分級level5.txt',
        '高中分級level6.txt',
        '新多益核心單字.txt',
        '國小基礎單字.txt',
        '國中基礎單字.txt',
        '國中進階單字.txt',
        '學測高頻單字.txt',
        '托福單字精選.txt',
        '雅思單字精選.txt',
        '全民英檢初級.txt',
        '全民英檢中高級.txt',
        '全民英檢中級.txt'
    ]
    
    for file_name in file_name_list:
        one_book_word_list = []
        with open("book/book/"+file_name, "rt") as file:
            word_list = file.readlines()
            c = 0 #記錄用走訪數
            a = len(word_list) #記錄用總數
            for word in word_list:
                c += 1
                if word=="":
                    continue
                
                result = loadHtml(word.strip('\n'))
                if result.count() >= 1:
                
                    try:
                        word_dict = analyze_html(result[0]['html'])
                    except Exception as e:
                        logCrawlProgress(str(e))
                        logCrawlProgress("error "+ word)
                    
                    if word_dict != None:
                        one_book_word_list.append(word_dict)
                else:
                    logCrawlProgress("no found in DB: "+ word)
                    
                if c%300 == 1:
                    logCrawlProgress("book:{} pos:{} of {}".format(file_name, c, a))
            
            #json結構
            json_dict = {'count': len(one_book_word_list), 'data':one_book_word_list}
            
            #可輸出非ascii字元, 縮排4字元寬度, 有序的
            json_str = json.dumps(json_dict, ensure_ascii=False, indent=4, sort_keys=True)
            
            #輸出json
            with open("book/json/"+file_name.strip('.txt')+".json" , "wt") as file:
                file.write(json_str)

#找某一單字在哪一個單字檔中
def findOneWord(word_name):
    for file_name in file_name_list:
        if not file_name.endswith(".txt"):
            continue
        with open("book/book/"+file_name, "rt") as file:
            word_list = file.readlines()
            if word_name+"\n" in word_list or word_name in word_list:
                print((word_name, file_name))


#檢查所有json檔的所有欄位是否包含空值, 列出相關欄位數
def check_json_file():
    count = 0 #單字走訪數
    check_list = {} #各欄位累積空值數
    word_column_tuple_list = [] #包含空值欄位的單字詳情
    
    json_file_list = os.listdir("book/json")#所有json檔
    
    for json_file in json_file_list:
        
        if(not json_file.endswith(".json")):
            break
            
        with open("book/json/"+json_file, 'rt') as file:     
            
            json_text = file.read()
            file_dict = json.loads(json_text)
            
            for word in file_dict['data']:
                count += 1
                
                for key in word:
                    if word[key] == "":
                        if key not in check_list :
                            check_list[key] = 0
                        else:
                            check_list[key] += 1

                    if key == "audio_url" or key == "pronunciation":
                        word_column_tuple_list.append((count, word['word_name'], word['audio_url'], word['pronunciation']))
                        
                        
    print(check_list)
    print(count)
    print(word_column_tuple_list)