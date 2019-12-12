from flask import Flask, jsonify, request, render_template
from redis import Redis
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
r = Redis(host='redis', port=6379)
socketio = SocketIO(app)


"""
初期化
"""

status_nums = (0, 1, 2, 3, 4, 5, 6)
# status_numsについて
# 0: 準備中
# 1: トータライザ
# 2: クイズ
# 3: 終了

r.set('status', 0)


"""
ページ
"""

@app.route('/')
def index():
  status = int(r.get('status'))
  if status == 0:
    return render_template('wait.html')
  elif status == 1:
    return render_template('vote.html')
  elif status == 2:
      return render_template('blackout.html')
  elif status in [3, 4, 5]:
    return render_template('quiz.html', quiz_num = str(status-3))
  elif status == 6:
    return render_template('ED.html')
  else:
    return "status error"

# 管理者用ページ
@app.route('/gCWZKf4B')
def test():
  return render_template('test.html')


"""
WebSocket
"""

@socketio.on('connect')
def socket_connect():
  send('Connected', namespace='/socket')

@socketio.on('message')
def socket_send_message(message):
  send(message, namespace='/socket', broadcast=True)

# メッセージの送信
@app.route('/api/gCWZKf4B/socket', methods=['POST'])
def send_message():
  data = request.get_json()
  if data['key'] != 'ChQUATbZ':
    return jsonify({'message': 'NG'})
  else:
    socket_send_message(data['message'])
    return jsonify({'message': 'SENT'})


"""
ユーザに公開するAPI
"""

# 状態を確認
@app.route('/api/status', methods=['GET'])
def get_status():
  return jsonify({'status': int(r.get('status'))})  # statusの数値を返す

# 投票
@app.route('/api/vote', methods=['POST'])
def vote():
  r.sadd('addr', request.headers.getlist("X-Forwarded-For")[0])  # ユーザのIPアドレスを集合'addr'に追加
  return jsonify({'message': 'VOTED'})


"""
管理者に公開するAPI
"""

# ステータスの変更
@app.route('/api/gCWZKf4B/status', methods=['POST'])
def change_status():
  data = request.get_json()
  if data['key'] != 'ChQUATbZ':
    return jsonify({'message': 'NG'})
  elif data['status'] not in status_nums:
    return jsonify({'message': 'NG'})
  else:
    r.set('status', data['status'])
    return jsonify({'message': 'CHANGED'})

# 投票状況の確認
@app.route('/api/gCWZKf4B/vote', methods=['GET','DELETE'])
def manage_vote():
  if request.method == 'DELETE':
    data = request.get_json()
    if data['key'] != 'ChQUATbZ':
      return jsonify({'message': 'NG'})
    r.delete('addr')  # 集合'addr'を削除
    socket_send_message('RESET')
    return jsonify({'message': 'DELETED'})
  else:
    return jsonify({'num': int(r.scard('addr'))})  # 集合'addr'の要素数を返す


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
  socketio.run(app)
