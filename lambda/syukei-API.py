import json
import boto3
from collections import defaultdict

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB設定
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')

table_map = {
    "dai1mon": "webd-quiz-no1",
    "dai2mon": "webd-quiz-no2",
    "dai3mon": "webd-quiz-no3",
    "dai4mon": "webd-quiz-no4",
    "dai5mon": "webd-quiz-no5"
}

def lambda_handler(event, context):

    # ① Lambda関数の先頭にログを追加して、イベントが届いているか確認
    logger.info(f"Lambda triggered. Raw event: {json.dumps(event)}")

    try:
        # event['body'] の中身が空かどうかをログで確認
        body_raw = event.get('body', '')
        if not body_raw:
            raise ValueError("Request body is empty")

        logger.info(f"event['body']: {body_raw}")
        data = json.loads(body_raw)

        # JSON形式のbodyを辞書に変換
    #    data = json.loads(event['body'])

        # テーブル名を取得
        quizNo = data.get('quizNo', '')
        table_name = table_map.get(quizNo)
        table = dynamodb.Table(table_name)

        # answerとteamを取得
        correct_answer = data.get('correct_answer', '')

        # 例：ログ出力
        logger.info(f"quizNo: {quizNo}, table_name: {table_name}, correct_answer: {correct_answer}")

        if not correct_answer:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'correct_answer is required'}),
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            }

        response = table.scan()
        items = response.get('Items', [])

        team_stats = defaultdict(lambda: {'correct': 0, 'total': 0})

        for item in items:
            team = str(item.get('team'))
            user_answer = item.get('answer')

            if team is not None and user_answer is not None:
                team_stats[team]['total'] += 1
                if user_answer == correct_answer:
                    team_stats[team]['correct'] += 1

        result = {}
        for team, stats in team_stats.items():
            correct = stats['correct']
            total = stats['total']
            accuracy = round((correct / total) * 100, 2) if total > 0 else 0
            result[str(team)] = {
                'correct': correct,
                'total': total,
                'accuracy_percent': accuracy
            }

        return {
            'statusCode': 200,
            'body': json.dumps(result),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }

    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }