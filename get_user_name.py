medicine_list=['アミトリプチリン', 'イミプラミン', 'スルモンチール', 'アナフラニール', 'アモキサン', 'アンプリット', 'プロチアデン', 'ルジオミール', 'クロンモリン', 'マプロミール', 'テトラミド', ...(中略)...,'リフレックス', 'レメロン', 'スルピリド', 'ドグマチール', 'ミラドール', 'アビリット', 'マーゲノール', 'ベタナミン']


import json
from requests_oauthlib import OAuth1Session


CK = "*******" #API key
CS = "*******" #Consumer_secret
AT = "*******" #Access_token
ATS = "*******" #Access_secret
twitter = OAuth1Session(CK, CS, AT, ATS)

url = 'https://api.twitter.com/1.1/search/tweets.json' #ツイート検索用

users = [] #検索したscreen_nameを格納するリスト

#関数の作成（入力が薬剤名リスト、出力がユーザー名のリスト）
def screen_name_from_medicine(medicine_list):
    for i in range(len(medicine_list)):
        medicine = medicine_list[i] #薬剤名リストから薬剤名を取り出す
        params = {'q': medicine, #この薬剤名を含むツイートを検索
                  'result_type':'mixed', #ツイート検索はランダム（新しい順などではない）
                  'count': 20, #一つの薬剤名あたり取得するツイートの数
                  'lang':'ja' #日本語のツイートを検索
                 }

        req = twitter.get(url, params = params)

        if req.status_code==200: #もしresponseが成功なら、req.status_code=200である
            res = json.loads(req.text)
            for line in res['statuses']:
                screen_name=line['user']['screen_name']
                if ('bot' not in screen_name) and (screen_name not in users):
                 #screen_nameに'bot'を含む物はusersリストに含めない
                 #usersリストに重複がないようにする
                    users.append(screen_name)

#関数の使用
screen_name_from_medicine(medicine_list)
#作成したリストを出力
print(users)
