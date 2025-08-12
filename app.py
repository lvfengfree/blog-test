from flask import Flask, jsonify, request, session
import pymysql
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'blogtest'  # 用于session加密，务必换成复杂安全的字符串
CORS(app, supports_credentials=True)  # 允许跨域，并支持携带cookie

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_NAME = 'test'

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 登录接口（用MySQL验证用户名密码）
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "用户名和密码不能为空"}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()
        conn.close()

        if user and user['password'] == password:
            session["username"] = username
            return jsonify({"message": "登录成功"})
        else:
            return jsonify({"message": "用户名或密码错误"}), 401

    except Exception as e:
        return jsonify({"message": f"服务器错误: {str(e)}"}), 500

@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return jsonify({"message": "已登出"})

@app.route("/api/check_login")
def check_login():
    if "username" in session:
        return jsonify({"logged_in": True, "username": session["username"]})
    else:
        return jsonify({"logged_in": False})

# 获取文章列表
@app.route("/api/getWordList")
def getWordList():
    try:
        conn = get_db_connection()
        sql = "SELECT * FROM word_info"
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"message": f"服务器错误: {str(e)}"}), 500

# 根据 slug 获取单篇文章
@app.route('/api/article/<slug>')
def get_article(slug):
    try:
        conn = get_db_connection()
        sql = "SELECT * FROM word_info WHERE link LIKE %s"
        with conn.cursor() as cursor:
            cursor.execute(sql, ('%' + slug,))
            article = cursor.fetchone()
        conn.close()

        if article:
            return jsonify(article)
        else:
            return jsonify({"message": "文章不存在"}), 404
    except Exception as e:
        return jsonify({"message": f"服务器错误: {str(e)}"}), 500

# 修改文章接口，PUT 请求
@app.route('/api/article/<slug>', methods=['PUT'])
def update_article(slug):
    if "username" not in session:
        return jsonify({"message": "未登录"}), 401

    data = request.json
    title = data.get('title')
    introduction = data.get('introduction')
    link = data.get('link')
    word = data.get('word')
    text_pinyin = data.get('text_pinyin')

    if not title or not introduction or not link or not word:
        return jsonify({'message': '缺少必要字段'}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 检查文章是否存在
            sql_check = "SELECT * FROM word_info WHERE link LIKE %s"
            cursor.execute(sql_check, ('%' + slug,))
            article = cursor.fetchone()
            if not article:
                return jsonify({'message': '文章不存在'}), 404

            sql_update = """
                UPDATE word_info
                SET title=%s, introduction=%s, link=%s, word=%s, put_time=NOW(), text_pinyin=%s
                WHERE link LIKE %s
            """
            cursor.execute(sql_update, (title, introduction, link, word, text_pinyin, '%' + slug))
            conn.commit()
        conn.close()

        return jsonify({'message': '更新成功'})
    except Exception as e:
        return jsonify({'message': f'服务器内部错误: {str(e)}'}), 500
@app.route('/api/article', methods=['POST'])
def add_article():
    data = request.get_json()
    title = data.get('title')
    introduction = data.get('introduction')
    link = data.get('link')
    word = data.get('word', '')
    text_pinyin = data.get('text_pinyin', '')

    if not title or not introduction or not link:
        return jsonify({'message': '标题、简介和链接不能为空'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO word_info (title, introduction, link, put_time, word, text_pinyin)
        VALUES (%s, %s, %s, NOW(), %s, %s)
        """
        cursor.execute(sql, (title, introduction, link, word, text_pinyin))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': '文章添加成功'}), 201

@app.route('/api/article/<string:title>', methods=['DELETE'])
def delete_article(title):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM word_info WHERE title = %s"
        cursor.execute(sql, (title,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'message': '文章不存在'}), 404
        return jsonify({'message': '文章删除成功'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
