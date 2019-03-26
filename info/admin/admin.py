from flask import Blueprint,render_template,request,flash,redirect,url_for,session,jsonify
from models import *
from utils.constand import admin_news_count
from utils.response_code import RET,error_map
import re
#生成密码
from werkzeug.security import generate_password_hash,check_password_hash
#初始化
admin_blue = Blueprint('admin',__name__)

#显示登陆页面
@admin_blue.route("/login",methods=['post','get'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username)
        print(password)
        if not all([username,password]):
            flash('用户名和密码都必须输入')
        else:
            #用户名必须是数字，字母下划线5到8位
            flag = re.match("\w{5,8}$",username)
            # print(flag)
            if flag == False:
                flash('用户名不合法')
            else:
                admin = Admin.query.filter(Admin.name==username).first()
                if not admin:
                    flash('用户不存在')
                else:
                    flag = check_password_hash(admin.password_hash,password)
                    if flag:
                        session['username'] = username
                        return redirect(url_for('admin.index'))
                    else:
                        flash("密码错误")
    return render_template('admin/login.html')

#初始化管理员
@admin_blue.route("/addadmin")
def add_admin():
    password = generate_password_hash('123')
    admin = Admin(name='admin',password_hash=password)
    db.session.add(admin)
    return 'ok'
# 显示后台管理页面
@admin_blue.route('/index')
def index():
    admin_user = session.get('username')
    if not admin_user:
        return redirect(url_for('info.admin.admin.login'))
    else:
        return render_template('admin/index.html')

#点击新闻管理跳转的新闻管理分类页面，直接渲染出新闻管理分类页面
@admin_blue.route('/newscate',methods=['post','get'])
def newscate():
    if request.method == 'POST':
        mes = {}
        id = request.form.get('id')
        name = request.form.get('name')
        if id:
            news_type = News_type.query.filter(News_type.id==id).first()
            if not news_type:
                mes['code'] = 10050
                mes['message'] = '没有此类信息'
            else:
                news_type.name=name
                db.session.add(news_type)
                mes['code'] = 200
                mes['message'] = '修改成功'
                return jsonify(mes)
        else:
            if name:
                category=News_type.query.filter(News_type.name==name).first()
                if category:
                    mes['code']=10010
                    mes['message'] = '分类以存在'
                    return jsonify(mes)
                else:
                    news_type=News_type(name=name)
                    print(db)
                    db.session.add(news_type)
                    mes['code'] = 200
                    mes['message'] = '添加成功'
                    print(news_type)
                    return jsonify(mes)
            else:
                mes['code'] = 10020
                mes['message'] = '不能为空'
                return jsonify(mes)
    category=News_type.query.all()
    return render_template('admin/news_type.html',category=category)

#新闻分类删除
@admin_blue.route("/deletecate",methods=['post','get'])
def deletecate():
    mes = {}
    if request.method == "POST":
        id=request.form.get('id')
        news_type=News_type.query.filter(News_type.id==id).delete()
        mes['code'] = 200
        mes['message'] = '删除成功'
        return jsonify(mes)

# 新闻分页,搜索列表
@admin_blue.route('/newsreview')
def newsreview():
    current_page = 1
    try:
        page = int(request.args.get('page',0))
    except:
        page = 0
    keyword = request.args.get('keyword')
    #分页
    if page>0:
        current_page = page
    page_count = admin_news_count
    #搜索
    if keyword:
        news_list = News.query.filter(News.name.like('%'+keyword+'%')).paginate(current_page,page_count,False)
    else:
        keyword=''
        news_list = News.query.paginate(current_page,page_count,False)
    data = {'news_list':news_list.items,'current_page':news_list.page,'total_page':news_list.pages,'keyword':keyword}

    return render_template('admin/news_review.html',data=data)

# #审核
# @admin_blue.route("/news_review_detail",methods=['post','get'])
# def news_review_detail():
#     if request.method == 'POST':
#         mes = {}
#         #获取要更新的值
#         id = request.form.get('id')
#         action = request.form.get('action')
#         reason = request.form.get('reason')
#         print(action)
#         #通过ID获取新闻
#         news = News.query.filter(News.id == id).first()
#         if news:
#             #在审核成功的时候更新字段
#             news.id_exam = int(action)
#             #在审核失败的时候更新原因
#             if int(action) == 2:
#                 news.reason = reason
#             db.session.add(news)
#             mes['errno'] = 200
#             mes['errmsg'] = '审核成功'
#         else:
#             mes['errno'] = 10020
#             mes['errmsg'] = '找不到该新闻' 
#         return jsonify(mes)
#     id = request.args.get('id')
#     news = News.query.filter(News.id == id).first()
#     data = {'news':news}
#     return render_template("admin/news_review_detail.html",data=data)


# 审核
@admin_blue.route("/news_review_detail",methods=['post','get'])
def news_review_detail():
    if request.method=='POST':
        mes={}
        # 需要更新的值
        id = request.form.get('id')
        action = request.form.get('action')
        reason = request.form.get('reason')
        # 通过id获取新闻
        news = News.query.filter(News.id==id).first()
        if news:
            # 存在更新字段
            news.is_exam = int(action)
            # 失败的时候更新原因
            if int(action) == 2:
                news.reason = reason
            db.session.add(news)
            mes['errno'] = RET.OK
            mes['errmsg'] = error_map[RET.OK]
        else:
            mes['errno'] = 10010
            mes['errmsg'] = '找不到新闻'
        return jsonify(mes)
    id = request.args.get('id')
    news = News.query.filter(News.id==id).first()
    data ={'news':news}
    return render_template('admin/news_review_detail.html',data=data)

from datetime import timedelta
@admin_blue.route("/user_count",methods=['post','get'])
def user_count():
    #获取总人数
    total = User.query.count()
    #每月活跃人数，从当月一号到现在
    monthday = datetime.strftime(datetime.now(),"%Y-%m-01")
    month_total = User.query.filter(User.update_time>=monthday).count()
    #每月活跃人数，从早晨00到现在
    day = datetime.strftime(datetime.now(),"%Y-%m-%d")
    day_total = User.query.filter(User.update_time>=day).count()
    datelist = []
    daycount = []
    for i in range(30,0,-1):
        startime = datetime.strptime(day,'%Y-%m-%d') - timedelta(i)
        endtime = datetime.strptime(day,'%Y-%m-%d') - timedelta(i-1)
        dayc = User.query.filter(User.update_time>=startime,
        User.update_time<=endtime).count()
        datelist.append(datetime.strftime(startime,"%Y-%m-%d"))
        daycount.append(dayc)
    data = {'total':total,'month_total':month_total,'day_total':day_total,
    'datelist':datelist,'daycount':daycount}
    return render_template('admin/user_count.html',data=data)


@admin_blue.route("/user_list")
def user_list():
    data = []
    return render_template("admin/user_list.html",data=data)
