# coding=utf-8

import sys
import json
import base64
import os

# QQ:376383538/微信：XzDz0816
# 保证兼容python2以及python3
IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
else:
    import urllib2
    from urllib import quote_plus
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode

# 防止https证书校验不正确
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


from tts import get_mp3



API_KEY = 'tGzYt1z9YPbHU22w6VfPOYKf'

SECRET_KEY = 'epCCvZuTKqw0QC3gYA6pCjhNQRdAXZzo'



BASE_DIR = os.path.dirname(os.path.abspath(__file__))



OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"


"""  TOKEN start """
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'


"""
    获取token
"""
def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    if (IS_PY3):
        result_str = result_str.decode()


    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print ('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print ('please overwrite the correct API_KEY and SECRET_KEY')
        exit()

"""
    读取文件
"""
def read_file(image_path):
    f = None
    try:
        f = open(image_path, 'rb')
        return f.read()
    except:
        print('read image file fail')
        return None
    finally:
        if f:
            f.close()


"""
    调用远程服务
"""
def request(url, data):
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        if (IS_PY3):
            result_str = result_str.decode()
        return result_str
    except  URLError as err:
        print(err)


def get_text(file_path):
    # 获取access token
    token = fetch_token()

    # 拼接通用文字识别高精度url
    image_url = OCR_URL + "?access_token=" + token

    text = ""

    # 读取书籍页面图片
    file_content = read_file(file_path)

    # 调用文字识别服务
    result = request(image_url, urlencode({'image': base64.b64encode(file_content)}))

    # 解析返回结果
    result_json = json.loads(result)
    for words_result in result_json["words_result"]:
        text = text + words_result["words"]

    # 打印文字
    # print(text)
    return text, file_content


def start():
    file_list = []
    data = os.walk(os.path.join(BASE_DIR, "input"))
    for parent, dir_names, file_names in data:
        print("{}\n{}\n{}".format(parent, dir_names, file_names))
        for file_name in file_names:
            # if file_name.split(".")[-1] == tp:
            file_path = os.path.join(parent, file_name)
            print("    {}".format(file_path))
            # file_tree = file_tree+file_path+'\n'
            file_list.append(file_path)
        break
    for file_path in file_list:
        try:
            text, file_content = get_text(file_path)
            _file_path = file_path.replace("input", "output")
            with open(_file_path, "wb") as f:
                f.write(file_content)
            with open(_file_path+".txt", "w") as f:
                f.write(text)
            get_mp3(text, _file_path)
            os.remove(file_path)
        except Exception as error:
            print(error)



if __name__ == '__main__':
    start()
