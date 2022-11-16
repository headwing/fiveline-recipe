from flask import Flask, render_template, request, jsonify, session, redirect, url_for
app = Flask(__name__)
import certifi
ca=certifi.where()
from pymongo import MongoClient
client = MongoClient("mongodb+srv://YouJung:sparta@cluster0.f8q7bml.mongodb.net/?retryWrites=true&w=majority")
db = client.FLR
import jwt

import datetime
import hashlib
SECRET_KEY = 'SPARTA'

@app.route('/')
def upload():
   return render_template('upload.html')

@app.route("/FLR", methods=["POST"])
def recipe_post():
    recipe_receive = request.form['title_give']
    cookingtime_receive = request.form['cookingtime_give']
    content1_receive = request.form['content1_give']
    content2_receive = request.form['content2_give']
    content3_receive = request.form['content3_give']
    content4_receive = request.form['content4_give']
    content5_receive = request.form['content5_give']
    star_receive = request.form['star_give']
    image_receive = request.form['image_give']
    post_list = list(db.post.find({}, {'_id': False}))
    count = len(post_list) + 1


    doc = {
        'recipe': recipe_receive,
        'cookingtime': cookingtime_receive,
        'content1': content1_receive,
        'content2': content2_receive,
        'content3': content3_receive,
        'content4': content4_receive,
        'content5': content5_receive,
        'page':count,
        'star':star_receive,
        'image': image_receive
    }

    db.post.insert_one(doc)

    return jsonify({'msg': '작성 완료!'})


@app.route("/FLR/user", methods=["GET"])
def api_valid():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})




if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)