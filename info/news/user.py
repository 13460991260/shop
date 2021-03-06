from flask import Blueprint,render_template,jsonify,g,session,make_response,request,redirect,url_for
from utils.captcha.captcha import captcha
from models import *
from werkzeug.security import generate_password_hash,check_password_hash
from utils.comm import isLogin
from utils.constand import admin_news_count
from apps import photos
user_blue = Blueprint('user',__name__)

#展示首页
@user_blue.route("/get_image")
def get_image():
    name,text,image_url = captcha.generate_captcha()
    session['image_code'] = text.upper()
    response = make_response(image_url)
    response.headers['Content-Type'] = 'image/jpg'
    return response

@user_blue.route("/index")
def index():
    return render_template('news/text.html')

#注册用户
@user_blue.route("/register",methods=['post'])
def register():
    print(request.form)
    mes={}
    mobile = request.form.get('mobile',0)
    password = request.form.get('password','')
    sms_code = request.form.get('sms_code','')
    try:
        agree = int(request.form.get('agree'))
    except:
        agree = 2
    print(mobile+"##"+password+"##"+sms_code+"##"+str(agree))
    if not all([mobile,password,sms_code,agree]):
        mes['code'] = 10010
        mes['message'] = '参数不完整'
    else:
        #是否同意协议
        if agree == 1:
            #判断图片验证码是否正确
            imagecode = session.get('image_code')
            if imagecode.upper() != sms_code.upper():
                mes['code'] = 10040
                mes['message'] = '验证码不匹配'
            else:
                password = generate_password_hash(password)
                user = User(nick_name=mobile,password_hash=password,mobile=mobile)
                print(user)
                db.session.add(user)
                session['username'] = mobile
                mes['code'] = 200

                mes['message'] = '验证成功'
        else:
            mes['code'] = 10020
            mes['message'] = "必须同意"
    return jsonify(mes)

#显示用户中心
@user_blue.route("/user_info")
@isLogin
def user_info():
    user = g.user
    data = {'user_info':user}
    return render_template('news/user.html',data=data)

#登录
@user_blue.route("/login",methods=["post",'get'])
def login():
    mes = {}
    if request.method == "POST":
        username = request.form.get('mobile')
        password = request.form.get('password')
        print(username)
        print(password)
        if not all([username,password]):
            mes['code'] = 10010
            mes['message'] = '用户密码不能为空'
        else:
            user = User.query.filter(User.mobile==username).first()
            if not user:
                mes['code'] = 10011
                mes['message'] = '用户不存在'
            else:
                flag = check_password_hash(user.password_hash,password)
                if flag:
                    session['username'] = username
                    session['user_id'] = user.id
                    mes['code'] = 200
                    mes['message'] = '登录成功'
                else:
                    mes['code'] = 10020
                    mes['message'] = '用户或密码错误'
    return jsonify(mes)

#退出登录
@user_blue.route("/logout")
def logout():
    mes={}
    session.pop('username',None)
    mes['code'] = 200
    return redirect("/")


#显示密码修改页面
@user_blue.route('/pass_info',methods=['post','get'])
def pass_innfo():
    username = session.get("username")
    if not username:
        return redirect(url_for('news.index'))
    else:
        user = User.query.filter(User.mobile == username).first()                     
        if request.method == "POST":
            mes = {}
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            new_password2 = request.form.get('new_password2')
            if new_password != new_password2:
                mes['code'] = 10010
                mes['message'] = '两次密码输入不一致'
                return jsonify(mes)
            else:
                user=User.query.filter(User.id==user.id).first()
                password=user.password_hash
            if not check_password_hash(password,old_password):
                mes['code']=10520
                mes['message']="老密码输入不正确"
            else:
                User.query.filter(User.id==user.id).update({'password_hash':generate_password_hash(new_password2)})
                mes['code']= 200
                mes['message']= '修改成功'
            return jsonify(mes)
    return render_template('news/user_pass_info.html')

#显示修改个人资料页面
@user_blue.route("/base_info",methods=['post','get'])
@isLogin
def base_info():
    user = g.user
    if request.method == 'POST':
        signature = request.form.get("signature")
        nick_name = request.form.get("nick_name")
        gender = request.form.get("gender")
        joy = request.form.get("joy")
        language = request.form.get("language")
    
        user.nick_name = nick_name
        user.signature = signature
        user.gender=gender
        user.joy = joy
        user.language = int(language)
        db.session.add(user)
    jlist = []
    if user.joy:
        jlist = [int(i) for i in user.joy.split(",")]
    joylist = [{'id':1,'name':'唱歌'},{'id':2,'name':'跳舞'},{'id':3,'name':'看书'}]
    data = {'user_info':user,'joylist':joylist,'jlist':jlist}
    # print(data)
    return render_template("news/user_base_info.html",data=data)


#上传头像
@user_blue.route("/pic_info",methods=['post','get'])
def pic_info():
    username = session.get("username")
    if not username:
        return redirect(url_for('news.index'))
    else:
        
        user = User.query.filter(User.mobile == username).first()        
        if request.method == "POST":
            image = request.files['avatar']
            file_name = photos.save(image)
            #更新数据库
            user.avatar_url = "/static/upload/"+file_name
            db.session.add(user)
        data = {'user_info':user}


        return render_template("/news/user_pic_info.html",data=data)

# 新闻发布
@user_blue.route("/news_release",methods=['post','get'])
@isLogin
def news_release():
    userid = g.user.id
    if request.method == "POST":
        data = request.form
        title = data.get('title','')
        category_id = data.get('category_id',0)
        digest = data.get('digest','')
        content = data.get('content','')
        image = request.files['index_image']
        image_url = ""
        if image:
            image_name = photos.save(image)
            image_url = "static/upload/"+image_name
        news = News(name=title,cid=category_id,content=content,image_url=image_url,descrp=digest,is_exam=0,reason='',user_id=userid)
        db.session.add(news)
        return redirect(url_for('user.news_list'))
    cate = News_type.query.all()
    data = {'cate':cate}
    return render_template("news/user_news_release.html",data=data)

#新闻列表
@user_blue.route("/news_list")
@isLogin
def news_list():
    user = g.user
    current_page = 1
    try:
        page = int(request.args.get('page',0))
    except:
        page = 0

    #分页
    if page>0:
        current_page = page
    page_count = admin_news_count
    news_list = News.query.paginate(current_page,page_count,False)
    data = {'news_list':news_list.items,'current_page':news_list.page,'total_page':news_list.pages}
     
    return render_template('news/user_news_list.html',data=data)


#图片上传
@user_blue.route("/upload_img")
def upload_img():
    image = request.files['file']
    file_name = photos.save(image)
    mes = {}
    mes['path'] = "/static/upload/"+file_name
    mes['error'] = False
    return jsonify(mes)
   

#我的收藏
@user_blue.route("/collection")
@isLogin
def collection():
    user = g.user
    current_page= request.args.get('p',1)
    page_count = 1
    collect = user.user_collect.paginate(int(current_page),page_count,False)
    data = {'news_list':collect.items,'current_page':collect.page,
    'total_page':collect.pages}
    return render_template("/news/user_collection.html",data=data)






