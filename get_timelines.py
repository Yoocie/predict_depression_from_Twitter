import tweepy
import config  #同じディレクトリに'config.py'というファイルがあります。

'''
config.py
CK = "*****" #CONSUMER_KEY
CS = "*****" #CONSUMER_SECRET
AT = "*****" #ACCESS_TOKEN
ATS = "*****" #ACCESS_TOKEN_SECRET
'''

CK = config.CK
CS = config.CS
AT = config.AT
ATS = config.ATS

# OAuth認証
auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, ATS)
api = tweepy.API(auth)


#1ユーザー分のタイムラインを取得し、テキストファイルとして保存する関数の定義
def get_timeline(name,i):
    #一人あたり最大3200件のツイートを取得
    pages = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    data = []
    for page in pages:
        results = api.user_timeline(screen_name=name,\
                                    include_rts=False,\#リツイートは取得しません。
                                    count=200,\#上限の200件ずつ、ツイートを取得します。
                                    page=page)
        for result in results:
            data.append(result.text)

    line=''.join(data)
    #タイムラインの内容を含むテキストファイルの作成、保存
    #テキストファイルの名前は '20191210_user3_^^^.text' というような形式
    with open('20191210_user'+str(i)+'_'+name+'.txt', 'wt') as f:
        f.write(line)
