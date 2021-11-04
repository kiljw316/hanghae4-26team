from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.sulmin


@app.route('/')
def main():
    alcohols = list(db.alcohols.find({}, {'_id': False}))
    return render_template("index.html", alcohols=alcohols)


@app.route('/detail')
def detail():
    name_receive = request.args.get('name_give')
    num_receive = request.args.get('num_give')
    alcohol = db.alcohols.find_one({"name": name_receive}, {"_id": False})
    return render_template("detail.html", alcohol=alcohol, num=num_receive)


@app.route('/sign-up', methods=['POST'])
def sign_up():
    name_receive = request.form['name_give']
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    doc = {
        'name': name_receive,
        'id': id_receive,
        'pw': pw_receive
    }
    db.users.insert_one(doc)
    return jsonify({'msg': '회원가입 성공'})


@app.route('/join')
def join():
    return render_template('join.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/sign-in', methods=['POST'])
def sign_in():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    user = db.users.find_one({"id": id_receive, 'pw': pw_receive})
    if user:
        return jsonify({'result': 'success', 'msg': '로그인 성공'})
    return jsonify({'result': 'fail', 'msg': '로그인 실패'})


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
