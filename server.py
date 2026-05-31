# server.py
# 실행 전 필요 라이브러리 설치: pip install flask

import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)
LEADERBOARD_FILE = "global_leaderboard.json"

def load_leaderboard() -> list[dict]:
    """로컬 JSON 파일에서 글로벌 순위표를 불러옵니다."""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("leaderboard", [])
    except (json.JSONDecodeError, IOError):
        return []

def save_leaderboard(leaderboard: list[dict]) -> None:
    """글로벌 순위표를 JSON 파일에 저장합니다."""
    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump({"leaderboard": leaderboard}, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"[서버 오류] 파일 저장 실패: {e}")

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """상위 10명의 순위표를 반환하는 GET API"""
    leaderboard = load_leaderboard()
    return jsonify({"leaderboard": leaderboard}), 200

@app.route('/api/leaderboard', methods=['POST'])
def post_score():
    """새로운 점수를 받아 순위표를 갱신하는 POST API"""
    data = request.get_json()
    
    if not data or "name" not in data or "score" not in data:
        return jsonify({"error": "Invalid data format. 'name' and 'score' are required."}), 400
        
    player_name = str(data["name"]).strip()
    score = int(data["score"])
    
    leaderboard = load_leaderboard()
    leaderboard.append({"name": player_name, "score": score})
    
    # 점수 기준 내림차순 정렬 후 상위 10명만 슬라이싱
    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)[:10]
    
    save_leaderboard(leaderboard)
    
    return jsonify({
        "message": "Score successfully registered.",
        "leaderboard": leaderboard
    }), 201

if __name__ == '__main__':
    # 호스트를 0.0.0.0으로 설정하여 외부 접속 허용 (포트 5000)
    app.run(host='0.0.0.0', port=5000, debug=True)