#!/usr/bin/env python
import io, sys,os
import hmac,base64
import urllib
import hashlib
import time

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

from flask import Flask, Response
from flask import request
import requests
import logging
import json
import locale
#locale.setlocale(locale.LC_ALL,"en_US.UTF-8")


app = Flask(__name__)


console = logging.StreamHandler()
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
formatter = logging.Formatter(fmt)
console.setFormatter(formatter)
log = logging.getLogger("flask_webhook_dingtalk")
log.addHandler(console)
log.setLevel(logging.DEBUG)

EXCLUDE_LIST = ['prometheus', 'endpoint']

@app.route('/')
def index():
    return 'Webhook Dingtalk by JackHe https://github.com/hejianlai/prometheus-webhook-dingtalk.git'

@app.route('/dingtalk/send/',methods=['POST'])

def hander_session():
    token = os.getenv('ROBOT_TOKEN')
    secret = os.getenv('ROBOT_SECRET')
    timestamp = int(round(time.time() * 1000))
    dingtalk_url = 'https://oapi.dingtalk.com/robot/send?access_token=%s&timestamp=%d&sign=%s' % (token, timestamp, make_sign(timestamp, secret))
    post_data = request.get_data()
    post_data = json.loads(post_data.decode("utf-8"))['alerts']
    post_data = post_data[0]
    messa_list = []
    messa_list.append('### 报警类型: %s' % post_data['status'].upper())
    messa_list.append('**startsAt:** %s' % post_data['startsAt'])
    for i in post_data['labels'].keys():
        if i in EXCLUDE_LIST:
            continue
        else:
            messa_list.append("**%s:** %s" % (i, post_data['labels'][i]))
    messa_list.append('**Describe:** %s' % post_data['annotations']['description'])

    messa = (' \\n\\n > '.join(messa_list))
    status = alert_data(messa, post_data['labels']['alertname'], dingtalk_url )
    log.info(status)
    return status

def alert_data(data,title,profile_url):
    headers = {'Content-Type':'application/json'}
    send_data = '{"msgtype": "markdown","markdown": {"title": \"%s\" ,"text": \"%s\"}}' %(title,data)  # type: str
    send_data = send_data.encode('utf-8')
    reps = requests.post(url=profile_url, data=send_data, headers=headers)
    return reps.text

def make_sign(timestamp, secret):
    """新版钉钉更新了安全策略，这里我们采用签名的方式进行安全认证
    https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq
    """
    secret_enc = bytes(secret, 'utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = bytes(string_to_sign, 'utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return sign

if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port='8080')
