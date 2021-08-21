# python-yahoo-word
從Yahoo抓取單字並存於MongoDB

1. 準備單字列表, 例如多益題庫.txt
    https://github.com/a0979470582/python-yahoo-word/blob/main/book/book/新多益核心單字.txt

2. 走訪單字列表, 從Yahoo字典搜尋單字並取得html, 先存於MongoDB
    參考main_get.py
    
3. 使用SoupBeautiful套件分析單字所需欄位後, 輸出Json格式檔案

輸出結果範例:
{
    "count": 1259,
    "data": [
        {
            "audio_url": "https://s.yimg.com/bg/dict/dreye/live/f/abide.mp3",
            "example": "vt.及物動詞\n1. （常用於否定句和疑問句）忍受，容忍\nI cannot abide the loud noise anymore. 我再也無法忍受這麼大的噪音。\n\n2. 頂住\nShe resolved to abide the pressure her superiors put on her. 她決心頂住上司們向她施加的壓力。\n\n3. 等候\nabide one's time 等待時機\n\nvi.不及物動詞\n1. 持續\nabide in somebody's love 繼續得到某人的愛\n\n2. 【古】逗留，住[（+at/in）]\nHe abided here for a month. 他在這兒住了一個月。",
            "pronunciation": "/ əˋbaɪd /",
            "synonyms": "同義詞\nvt. 等候；忍受\nwait, obey, endure, tolerate\n\nvi. 滯留；居住\nstay, remain, reside, dwell\n\n反義詞\n「vi. 滯留，停留」的反義字\nstart, depart, leave",
            "translation": "vt. (常用於否定句和疑問句)忍受，容忍。頂住 \nvi. 持續。【古】逗留，住[(+at/in)] ",
            "variation": "動詞變化：abode\n/  abided\n/ abode\n/  abided\n/ abiding",
            "word_name": "abide"
        },.....
    ]
}
