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
    # jwt 토큰 가져옴
    token_receive = request.cookies.get('mytoken')
    # db에서 술 리스트 추출(_id 제외)
    alcohols = list(db.alcohols.find({}, {'_id': False}))
    # index 페이지 렌더링, 술 리스트, 토큰 전달
    return render_template("index.html", alcohols=alcohols, token=token_receive)


@app.route('/detail')
def detail():
    # 술 이름 및 인덱스 번호를 가져옴
    name_receive = request.args.get('name_give')
    num_receive = request.args.get('num_give')
    # db에서 술 이름에 해당하는 데이터 추출(_id제외)
    alcohol = db.alcohols.find_one({"name": name_receive}, {"_id": False})
    # detail 페이지 렌더링, 술 데이터, 인덱스 번호 전달
    return render_template("detail.html", alcohol=alcohol, num=num_receive)


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # 이름, 패스워드 가져옴
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    # sha256으로 pw 암호화
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
    }
    # users 콜렉션에 저장
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # 유저이름 가져옴
    username_receive = request.form['username_give']
    # db에서 해당하는 유저가 있을 경우 True 아니면 False
    exists = bool(db.users.find_one({"username": username_receive}))
    # True or False 전달
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 유저이름, 패스워드 가져옴
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    # 받은 패스워드를 암호화
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    #  유저이름, 패스워드 결과 저장
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})
    # 유저가 존재할 경우
    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        # jwt 토큰화
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        # 토큰 전달
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/review', methods=['POST'])
def posting_review():
    # 작성자, 리뷰, 술이름, 날짜 가져옴
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
    # reviews 콜렉션에 저장
    db.reviews.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '리뷰 작성 성공'})


@app.route('/review', methods=['GET'])
def listing_review():
    # 술 이름 가져옴
    name_receive = request.args.get('name_give')
    # 해당 술에 쓰인 리뷰 리스트(날짜 역순, 최대 5개 제한) 추출
    reviews = list(db.reviews.find({'name': name_receive}, {'_id': False}).sort('date', -1).limit(5))
    return jsonify({'reviews': reviews})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
