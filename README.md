# python-yahoo-word
從Yahoo抓取單字並存於MongoDB

1. 準備單字列表, 例如多益題庫.txt
    https://github.com/a0979470582/python-yahoo-word/blob/main/book/book/新多益核心單字.txt

2. 走訪單字列表, 從Yahoo字典搜尋單字並取得html, 先存於MongoDB
    參考main_get.py
    
3. 使用SoupBeautiful套件分析單字所需欄位後, 輸出Json格式檔案

    輸出結果範例:
    https://github.com/a0979470582/python-yahoo-word/blob/main/book/json/新多益核心單字.json
