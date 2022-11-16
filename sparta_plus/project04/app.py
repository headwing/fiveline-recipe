
from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient
import certifi

ca=certifi.where()

# client = MongoClient("mongodb+srv://youngjunkim0330:R!adudwns0330@cluster0.fcostps.mongodb.net/?retryWrites=true&w=majority")
# db = client.FLR

# client = MongoClient("mongodb+srv://test:test@cluster0.15fhovx.mongodb.net/test", tlsCAFile=ca)
# db = client.dbsparta_plus_week4

client = MongoClient("mongodb://YouJung:sparta@ac-alf7myn-shard-00-00.f8q7bml.mongodb.net:27017,ac-alf7myn-shard-00-01.f8q7bml.mongodb.net:27017,ac-alf7myn-shard-00-02.f8q7bml.mongodb.net:27017/?ssl=true&replicaSet=atlas-7rq6ec-shard-0&authSource=admin&retryWrites=true&w=majority", tlsCAFile=ca)
db = client.FLR

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'SPARTA'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib


#################################
##  HTML을 주는 부분             ##
#################################
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('index.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/upload')
def upload():
   return render_template('upload.html')

@app.route('/showrecipe')
def showrecipe():
   return render_template('showrecipe.html')

#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/API/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id_receive})

    if result is None:
        db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail', 'msg': '중복된 아이디입니다.'})



# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/API/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된 pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=5)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)


##########메인페이지############
@app.route("/FLR", methods=["GET"])
def recipe_get():
    post_list = list(db.post.find({}, {'_id': False}))
    return jsonify({'posts':post_list})

##########업로드페이지############

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
        'image': image_receive,
        'count': count
    }

    db.post.insert_one(doc)

    return jsonify({'msg': '작성 완료!'})

####### 닉네임 가져오는 법 #############
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


########### 코멘트 저장하는 것 ##############
@app.route("/FLR/commentPosting", methods=["POST"])
def comment_post():
    comment_receive = request.form['comment_give']
    doc = {
        'comment': comment_receive
    }
    db.post.insert_one(doc)
    return jsonify({'msg': 'POST 게시 완료!'})

########### 저장된 게시물의 정보 불러오기 ########
@app.route("/present", methods=["POST"])
def post_get():
    title_receive = str(request.form['title_give'])
    posting_list = db.post.find_one({'recipe': title_receive}, {'_id': False})
    return jsonify({'present': posting_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)