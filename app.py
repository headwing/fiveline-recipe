from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient("mongodb://YouJung:sparta@ac-alf7myn-shard-00-00.f8q7bml.mongodb.net:27017,ac-alf7myn-shard-00-01.f8q7bml.mongodb.net:27017,ac-alf7myn-shard-00-02.f8q7bml.mongodb.net:27017/?ssl=true&replicaSet=atlas-7rq6ec-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client.FLR

import certifi
ca=certifi.where()

@app.route('/')
def home():
    return render_template('index.html')


@app.route("/FLR", methods=["POST"])
def web_FLR_post():
    comment_receive = request.form['comment_give']
    doc = {
        'comments' : comment_receive
    }
    db.comment.insert_one(doc)
    return jsonify({'msg': 'POST 게시 완료!'})


@app.route("/post", methods=["GET"])
def post_get():
    posting_list = list(db.post.find({}, {'_id': False}))
    return jsonify({'posting' : posting_list})

@app.route("/comment", methods=["GET"])
def comment_get():
    comments_list = list(db.comment.find({}, {'_id': False}))
    return jsonify({'comments' : comments_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)