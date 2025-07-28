from flask import Flask, request, jsonify, send_from_directory
import hashlib
import os
import base64
import pymysql

# Serve static files from /static/register and set static folder to parent directory
app = Flask(__name__)

# MySQL database config
MYSQL_HOST = os.environ.get("DATABASE_HOST", "db")
MYSQL_PORT = int(os.environ.get("DATABASE_PORT", 3306))
MYSQL_USER = os.environ.get("DATABASE_USER", "robocjk")
MYSQL_DB = os.environ.get("DATABASE_NAME", "robocjk")
MYSQL_PASSWORD = os.environ.get("DATABASE_PASSWORD", "")
VALIDATION_KEY = os.environ.get("INVITATION_KEY", "")


def hash_django_password(password, iterations=36000, algorithm="sha256"):
    # Generate 9 random bytes and base64-encode them (as salt)
    salt = base64.b64encode(os.urandom(9)).decode("utf-8").strip()

    # Derive key using PBKDF2
    dk = hashlib.pbkdf2_hmac(
        algorithm, password.encode("utf-8"), salt.encode("utf-8"), iterations, dklen=32
    )

    # Return the hash in Django's PBKDF2 format
    return (
        f'pbkdf2_{algorithm}${iterations}${salt}${base64.b64encode(dk).decode("utf-8")}'
    )


# Serve index.html at /register and /register/
@app.route("/register/")
def serve_index():
    return send_from_directory("./", "index.html")


@app.route("/register/submit", methods=["POST"])
def submit():
    if request.method != "POST":
        return jsonify({"status": "error", "message": "Cannot process the request"}), 404

    username = request.form.get("username")
    first_name = request.form.get("first-name")
    last_name = request.form.get("last-name")
    email = request.form.get("email")
    password = request.form.get("password")
    password_confirmation = request.form.get("password_confirmation")
    invitation = request.form.get("invitation")

    print(
        f"Received data: {username}, {first_name}, {last_name}, {email}, {password}, {password_confirmation}, {invitation}"
    )

    if not all(
        [
            username,
            first_name,
            last_name,
            email,
            password,
            password_confirmation,
            invitation,
        ]
    ):
        return jsonify({"status": "error", "message": "Please fill in all the fields"}), 400

    if invitation != VALIDATION_KEY:
        return jsonify({"status": "error", "message": "Invalid nvitation key"}), 400

    if not validate_email(email):
        return (
            jsonify({"status": "error", "message": "Please provide a valid email"}),
            400,
        )

    if password != password_confirmation:
        return jsonify({"status": "error", "message": "Password does not match"}), 400

    hashed_password = hash_django_password(password)

    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            charset="utf8mb4",
        )
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO auth_user (username, password, email, first_name, last_name, is_superuser, is_staff, is_active, date_joined) 
            VALUES (%s, %s, %s, %s, %s, 0, 0, 0, NOW())""",
            (username, hashed_password, email, first_name, last_name),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": f"数据库错误: {str(e)}"}), 500

    return jsonify({"status": "success", "message": "Successfully registered"}), 201


def validate_email(email):
    return "@" in email and "." in email


if __name__ == "__main__":
    app.run(debug=True)
