# python-yahoo-word
說明:

透過爬蟲工具 SoupBeautiful 套件，自動從 Yahoo 奇摩字典 取得特定單字的詳細資訊，並儲存在本地的 MongoDB 資料庫以供查詢。

流程: 
1. 首先準備一份英文單字列表, 例如 [多益題庫.txt ](https://github.com/a0979470582/python-yahoo-word/blob/main/book/book/新多益核心單字.txt)。
    
2. 接著這一份程式，會依照英文單字列表的順序，一一的在 Yahoo 奇摩字典進行搜尋，並將搜尋結果的 html 進行分析以取得單字的解釋、詞性、例句等資料, 並存於本地 MongoDB, 參考 [main_get.py](https://github.com/a0979470582/python-yahoo-word/blob/main/main_get.py)。

3. 最後我們 MongoDB 就擁有原單字列表中的每一個單字的中文解釋和例句，可做進一步使用。

    輸出結果範例 [新多益核心單字.json](https://github.com/a0979470582/python-yahoo-word/blob/main/book/json/新多益核心單字.json)
    
