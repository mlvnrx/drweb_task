import os
import hashlib
from flask import Flask, request, jsonify, send_file
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

from utils import get_file_path, init_db
from db import get_user

app = Flask(__name__)
auth = HTTPBasicAuth()

# Директория для хранения загруженных файлов
STORE_DIR = os.path.join(os.getcwd(), "store")


if not os.path.exists(STORE_DIR):
    os.makedirs(STORE_DIR)


@auth.verify_password
def verify_password(username, password):
    user = get_user(username)
    if user:
        if check_password_hash(user.get("password"), password):
            return username
    return None


@app.route("/upload", methods=["POST"])
@auth.login_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_data = file.read()
    file_hash = hashlib.sha256(file_data).hexdigest()
    file_dir = os.path.join(STORE_DIR, file_hash[:2])
    os.makedirs(file_dir, exist_ok=True)
    file_path = os.path.join(file_dir, file_hash)

    with open(file_path, "wb") as f:
        f.write(file_data)

    return jsonify({"hash": file_hash}), 201


@app.route("/download/<file_hash>", methods=["GET"])
def download_file(file_hash):
    file_path = get_file_path(STORE_DIR, file_hash)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return jsonify({"error": "File not found"}), 404


@app.route("/delete/<file_hash>", methods=["DELETE"])
@auth.login_required
def delete_file(file_hash):
    file_path = get_file_path(STORE_DIR, file_hash)
    print(file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"message": "File deleted"}), 200
    else:
        return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
