#!/usr/bin/env python
import io, sys,os
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

from flask import Flask
from flask import request
import requests
import logging
import json


app = Flask(__name__)


console = logging.StreamHandler()
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
formatter = logging.Formatter(fmt)
console.setFormatter(formatter)
log = logging.getLogger("flask_webhook_wechat")
log.addHandler(console)
log.setLevel(logging.DEBUG)

EXCLUDE_LIST = ['prometheus', 'endpoint']

@app.route('/')
def index():
    return 'Webhook Wechat by JackHe https://github.com/hejianlai'

@app.route('/wechat/send/',methods=['POST'])

def hander_session():
    token = os.getenv('ROBOT_TOKEN')
    wechat_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=%s' %token
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
    status = alert_data(messa,wechat_url )
    log.info(status)
    return status

def alert_data(data,wechat_url):
    headers = {'Content-Type':'application/json'}
    send_data = '{"msgtype": "markdown","markdown": {"content": \"%s\"}}' %data  # type: str
    send_data = send_data.encode('utf-8')
    reps = requests.post(url=wechat_url, data=send_data, headers=headers)
    return reps.text

if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port='8080')