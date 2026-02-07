from flask import Flask, request, jsonify
from waitress import serve  # production WSGI 서버
import json
import time
from datetime import datetime, timedelta
import threading
import os

app = Flask(__name__)

LICENSE_FILE = "licenses.json"
SESSION_TIMEOUT = 60  # 초 (사용 중인지 판단하는 기준)

lock = threading.Lock()

def load_licenses():
    if not os.path.exists(LICENSE_FILE):
        return {}
    with open(LICENSE_FILE, "r") as f:
        return json.load(f)

def save_licenses(data):
    with lock:
        with open(LICENSE_FILE, "w") as f:
            json.dump(data, f, indent=2)

def is_license_expired(lic):
    if lic["duration_days"] is None:
        return False  # 무기한
    start_date = datetime.strptime(lic["start_date"], "%Y-%m-%d")
    end_date = start_date + timedelta(days=lic["duration_days"])
    return datetime.now() > end_date

@app.route("/check_license", methods=["POST"])
def check_license():
    data = request.get_json()
    key = data.get("license_key")
    licenses = load_licenses()

    if key not in licenses:
        return jsonify({"status": "error", "message": "라이선스 키가 잘못됨"}), 400

    lic = licenses[key]

    if is_license_expired(lic):
        return jsonify({"status": "error", "message": "라이선스 사용 기간이 만료됨"}), 403

    now = time.time()
    if lic["in_use"] and now - lic["last_check"] < SESSION_TIMEOUT:
        return jsonify({"status": "denied", "message": "이미 사용 중"}), 403

    # 인증 성공
    lic["in_use"] = True
    lic["last_check"] = now
    save_licenses(licenses)
    return jsonify({"status": "ok", "message": "라이선스 인증 성공"})

@app.route("/release_license", methods=["POST"])
def release_license():
    data = request.get_json()
    key = data.get("license_key")
    licenses = load_licenses()

    if key in licenses:
        licenses[key]["in_use"] = False
        licenses[key]["last_check"] = 0
        save_licenses(licenses)
        return jsonify({"status": "ok", "message": "라이선스 해제 완료"})

    return jsonify({"status": "error", "message": "라이선스 키가 존재하지 않음"}), 400

if __name__ == "__main__":
    print("서버 실행 중...")
    serve(app, host="0.0.0.0", port=5000)
