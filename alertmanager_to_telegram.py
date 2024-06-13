from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# 配置 Telegram 相关参数

TELEGRAM_BOT_TOKEN = '6862082937:AAEIl6FdVpzKRKNuhfE-hYv2BtuQwt7i8xc'
TELEGRAM_CHAT_ID = '-4225521223'

def extract_nodename(text):
    # 使用正则表达式匹配 "nodename:" 后面跟着任意非空白字符的部分
    match = re.search(r'nodename:([^\s]+)', text)
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
            # status = alert.get('status', 'unknown')
            labels = alert.get('labels', {})
            annotations = alert.get('annotations', {})
            # alertname = labels.get('alertname', 'unknown')
            instance = labels.get('instance', 'unknown')
            summary = annotations.get('summary', '-')
            description = annotations.get('description', 'No description')
            nodename = extract_nodename(description)

            if status == 'firing':
                message = f"*告警:* {summary}\n*主机:* {nodename}\n*描述:* {description}"
            elif status == 'resolved':
                message = f"**已恢复**\n*恢复:* {summary}\n*主机:* {nodename}\n*描述:* {description}"
            # message = f"*告警:* {summary}\n*主机:* {instance}\n*描述:* {description}"
            send_message_to_telegram(message)
    
        return jsonify({'status': 'success'})
    except RetryAfter:
        sleep(30)
        send_message_to_telegram(message)
        return jsonify({'status': 'success'})
    except TimedOut as e:
        sleep(60)
        bot.sendMessage(chat_id=chatID, text=message)
        return jsonify({'status': 'success'})
    except NetworkError as e:
        sleep(60)
        bot.sendMessage(chat_id=chatID, text=message)
        return jsonify({'status': 'success'})
    except Exception as error:       
        bot.sendMessage(chat_id=chatID, text="Error: "+str(error))
        app.logger.info("\t%s",error)
        return jsonify({'status': 'fail'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)


""" 
版本说明：
1.0 初始版本
2.0 解决了summary的展示问题
3.0 新增恢复告警，将主机信息从IP转为节点名

alertmanager.yml配置如下

receivers:
  - name: 'telegram-webhook'
    webhook_configs:
      - url: 'http://your_server_ip:5001/webhook'
"""
