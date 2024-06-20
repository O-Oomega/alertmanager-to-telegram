from flask import Flask, request, jsonify
import time
import requests
import re

app = Flask(__name__)

# 配置 Telegram 相关参数

TELEGRAM_BOT_TOKEN = 'your token'
TELEGRAM_CHAT_ID = 'your chat id'

def extract_nodename(text):
    # ***nodename的提取和使用可自行修改***
    # 使用正则表达式匹配description中的 "nodename:" 后面跟着任意非空白字符的部分
    match = re.search(r'nodename:([^\s\]]+)', text)
    if match:
        return match.group(1)
    else:
        return None

def send_message_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, json=payload)
    return response

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("Received data:", data)
    
        alerts = data.get('alerts', [])
        for alert in alerts:
            status = alert.get('status', 'unknown')
            labels = alert.get('labels', {})
            annotations = alert.get('annotations', {})
            # alertname = labels.get('alertname', 'unknown')
            instance = labels.get('instance', 'unknown')
            summary = annotations.get('summary', '-')
            description = annotations.get('description', 'No description')

            # ***nodename的提取和使用可自行修改***
            nodename = extract_nodename(description)

            if status == 'firing':
                message = f"*告警:* {summary}\n*主机:* {nodename}\n*描述:* {description}"
            elif status == 'resolved':
                message = f"**已恢复**\n*恢复:* {summary}\n*主机:* {nodename}\n*描述:* {description}"
            # message = f"*告警:* {summary}\n*主机:* {instance}\n*描述:* {description}"
            send_message_to_telegram(message)
    
        return jsonify({'status': 'success'})
    except Exception as error:
        app.logger.info("\t%s",error)
        print(f"\t{error}\n")
        # requests库在连接失败时会进行多次重试，超过一定次数后才会抛出错误
        # 因此此处不写重新连接的功能
        return jsonify({'status': 'fail', 'reason': f"error: {error}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)


""" 
版本说明：
1.0 初始版本
2.0 解决了summary的展示问题
3.0 新增恢复告警，将主机信息从IP转为节点名
4.0 删除多余的运行错误处理

alertmanager.yml配置如下

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 30s
  repeat_interval: 30m
  receiver: 'telegram-webhook'
  routes:
    - match_re:
        severity: critical|warning|info
        continue: true
receivers:
  - name: 'telegram-webhook'
    webhook_configs:
      - url: 'http://localhost:5001/webhook'
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
  - source_match:
      severity: 'warning'
    target_match:
      severity: 'info'
    equal: ['alertname', 'dev', 'instance']
"""


