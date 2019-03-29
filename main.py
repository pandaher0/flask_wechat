# coding:utf-8
# Author:hxj

from flask import Flask, request, abort, render_template
import hashlib
import xmltodict
import time
import json
# python2 urllib2
# import urllib2
# python3 urllib.request
import urllib.request

WECHAT_TOKEN = 'pandaher0'
WECHAT_APPID = 'wx068134501ee93bf7'
WECHAT_APPSECRET = 'd09d526e5241027c293dd97960aab1c0'

app = Flask(__name__)


@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    """对接微信公众号服务器"""
    # 接收参数
    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')

    if not all([signature, timestamp, nonce]):
        abort(400)

    # 三个参数
    li = [WECHAT_TOKEN, timestamp, nonce]
    # 字典序排序
    li.sort()
    # 拼接字符串
    temp_str = ''.join(li)
    # 进行sha1加密,得到正确的签名值
    sign = hashlib.sha1(temp_str).hexdigest()

    if signature != sign:
        abort(403)
    else:
        if request.method == 'GET':
            echostr = request.args.get('echostr')
            return echostr
        elif request.method == 'POST':
            xml_str = request.data
            if not xml_str:
                abort(400)

            xml_dict = xmltodict.parse(xml_str)
            xml_dict = xml_dict['xml']
            msg_type = xml_dict.get('MsgType')

            if msg_type == 'text':
                resp_dict = {
                    'xml': {
                        'ToUserName': xml_dict.get('FromUserName'),
                        'FromUserName': xml_dict.get('ToUserName'),
                        'CreateTime': int(time.time()),
                        'MsgType': 'text',
                        'Content': xml_dict.get('Content')
                    }
                }
                resp_xml = xmltodict.unparse(resp_dict)
                return resp_xml
            else:
                resp_dict = {
                    'xml': {
                        'ToUserName': xml_dict.get('FromUserName'),
                        'FromUserName': xml_dict.get('ToUserName'),
                        'CreateTime': int(time.time()),
                        'MsgType': 'text',
                        'Content': 'byebye'
                    }
                }
                resp_xml = xmltodict.unparse(resp_dict)
                return resp_xml

    return


@app.route('/wechat/index')
def index():
    """用户访问"""
    # 拿取用户信息
    code = request.args.get('code')
    if not code:
        return u'缺失参数'
    # 向微信服务发起http请求 获取access_token
    # https://api.weixin.qq.com/sns/oauth2/access_token?appid=APPID&secret=SECRET&code=CODE&grant_type=authorization_code
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (
        WECHAT_APPID, WECHAT_APPSECRET, code)
    # 发起http请求 获取响应体对象
    response = urllib.request.urlopen(url)
    # 获取响应体数据
    json_str = response.read()
    resp_dict = json.loads(json_str)
    # 获取access_token
    if 'errcode' in resp_dict:
        return u'获取access失败'

    access_token = resp_dict.get('access_token')
    openid = resp_dict.get('openid')

    url = 'https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN' % (access_token, openid)

    response = urllib.request.urlopen(url)

    user_json_str = response.read()

    user_json_data = json.loads(user_json_str)

    if 'errcode' in user_json_data:
        return u'获取用户信息失败'

    return render_template('index.html', user=user_json_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
