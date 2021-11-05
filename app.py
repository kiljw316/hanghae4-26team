from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'SPARTA'

client = MongoClient('localhost', 27017)
db = client.sulmin


@app.route('/')
def main():
    token_receive = request.cookies.get('mytoken')
    alcohols = list(db.alcohols.find({}, {'_id': False}))
    return render_template("index.html", alcohols=alcohols, token=token_receive)


@app.route('/detail')
def detail():
    name_receive = request.args.get('name_give')
    num_receive = request.args.get('num_give')
    alcohol = db.alcohols.find_one({"name": name_receive}, {"_id": False})
    return render_template("detail.html", alcohol=alcohol, num=num_receive)


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/review', methods=['POST'])
def posting_review():
    person_receive = request.form['person_give']
    review_receive = request.form['review_give']
    alcohol_receive = request.form['alcohol_give']
    date_receive = request.form['date_give']
    doc = {
        'name': alcohol_receive,
        'author': person_receive,
        'review': review_receive,
        'date': date_receive
    }
    db.reviews.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '리뷰 작성 성공'})


@app.route('/review', methods=['GET'])
def listing_review():
    name_receive = request.args.get('name_give')
    reviews = list(db.reviews.find({'name': name_receive}, {'_id': False}).sort('date', -1).limit(5))
    return jsonify({'reviews': reviews})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
