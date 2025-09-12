#!/usr/bin/env python3
import cgi
import mysql.connector
from datetime import datetime
import os
from urllib.parse import parse_qs

# フォームデータ取得
form = cgi.FieldStorage()
answer_value = form.getvalue("answer")

# 現在時刻を取得（日本時間）
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# チームのパラメータを受けとる
query_string = os.environ.get('QUERY_STRING', '')
params = parse_qs(query_string)
team = params.get('team', [''])[0]  # 1:G,2:H,3:R,4:S

# DB接続情報（XREAの設定に合わせて変更）
db_config = {
    'host': 's325.xrea.com',
    'user': 'john711_wedd',
    'password': 'john',
    'database': 'john711_wedd',
    'charset': 'utf8'
}

# データベースに記録
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    sql = "INSERT INTO dai1mon (timestamp, answer, team) VALUES (%s, %s, %s)"
    cursor.execute(sql, (now, answer_value, team))
    conn.commit()
    cursor.close()
    conn.close()
    message = f"{answer_value} を {now} に記録しました。"
except Exception as e:
    message = f"エラー: {e}"

# レスポンス出力
print("Content-Type: text/html\n")
print(f"<html><body>{message}</body></html>")