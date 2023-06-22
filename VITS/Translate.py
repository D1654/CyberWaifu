import configparser
import requests 
import hashlib
import random
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
fyid= config['Translate_Baidu']['baidu_appid']
fykey=config['Translate_Baidu']['baidu_secretkey']

appid = fyid
secretKey = fykey

def Translate(content):
    salt = random.randint(1, 10)
    code = appid + content + str(salt) + secretKey
    sign = hashlib.md5(code.encode()).hexdigest()  # 签名

    api = "http://api.fanyi.baidu.com/api/trans/vip/translate"

    data = {
        "q": content,
        "from": "auto",
        "to": "jp",
        "appid": appid,
        "salt": salt,
        "sign": sign
    }

    response = requests.post(api, data)

    try:
        result = response.json()
        dst = result.get("trans_result")[0].get("dst")

    except Exception as e:
        dst = content

    finally:
        return dst


# content ="そろそろ寝なくちゃ"
# print(Translate(content))
