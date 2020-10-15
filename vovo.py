from flask import Flask,request, render_template, Response, url_for, redirect  # import render_template， 否则无法使用该函数returntemplate
from flask_cors import CORS
import time
import datetime
import base64
import hashlib
import re
import random
import os
import json
import configparser
from py import forum_sql as a_sql
from py import forum_image as forum_img
from py import forum_email as a_email



project_location = "{}\\".format(os.getcwd())

#设置template和static的位置
app = Flask(__name__, template_folder="templates", static_folder="static")

#修改jinja的起始标识与结束标识，避免和vue发生冲突
app.jinja_env.variable_start_string = '<<'
app.jinja_env.variable_end_string = '>>'

#跨域
CORS(app, resources=r'/*')


# LOGIN 页面开始
@app.route("/login/", methods=['GET',])
def login():
    # 如果session为空则返回LOGIN页面
    session = request.cookies.get("session")
    if session == None or len(session) != 32:
        return render_template("login.html")

    else:
        # 检测session是否可用，可用则跳转到HOME界面，不可用返回LOGIN界面
        database = a_sql.database(mysql_config)     # 连接数据库
        sql_check_session_valid = """\
        SELECT session FROM user \
        WHERE session = '{}' \
        AND TIMESTAMPDIFF(DAY, session_at, NOW()) < 7;\
        """.format(session)
        fb_check_session_valid = database.execute(sql_check_session_valid)

        # 返回的元组不为空则判定为session可用，返回空或Flase则判断session不可用
        if fb_check_session_valid:
            return redirect(url_for("home"))
        else:
            return render_template("login.html")            

# LOGIN 页面结束        


# API LOGIN 开始
@app.route("/api/login/", methods=['POST',])
def api_login():

    # 获取邮箱和密码
    student_email = request.form['email'] + "@gmail.com"
    student_pwd = request.form['pwd']

    # 初始化数据库操作
    database = a_sql.database(mysql_config)
    # 查找用户是否已注册，如果已注册则跳到主页
    sql_check_email_valid = """\
    SELECT email FROM user \
    WHERE email='{}';\
    """.format(student_email)
    fb_check_email_valid = database.execute(sql_check_email_valid)
    # fb_check_email_valid = database.select(sql_check_email_valid, 0)

    if fb_check_email_valid:        # 返回不为空元组
        # 该邮箱已注册，验证身份
        sql_check_user = """\
        SELECT email FROM user \
        WHERE email='{}' \
        AND password='{}';\
        """.format(student_email, student_pwd)
        fb_check_user = database.execute(sql_check_user)

        if fb_check_user:       # 身份验证通过
            # 为该用户更新一个session,并跳转到主页
            new_session = md5(fb_check_user[0] + str(int(time.time())))
            sql_update_session = """\
            UPDATE user SET session = '{}' \
            WHERE email = '{}';\
            """.format(new_session, fb_check_user[0])
            database.execute(sql_update_session)
            resp = Response(json.dumps({'code':'302', 'msg':'/'}))
            resp.set_cookie('session', new_session, max_age=604800, httponly=True)
            return resp
        else:       # 身份验证不通过
            resp = Response(json.dumps({'code':'ALG002', 'msg':'账户或密码错误'}))
            return resp

    elif fb_check_email_valid == ():        # 该邮箱不存在
        # 进入注册流程
        ## 先删除register表里的同email数据，防止冲突
        sql_delete_register = """\
        DELETE FROM register \
        WHERE email = '{}';\
        """.format(student_email)
        database.execute(sql_delete_register)

        # 根据邮箱和时间戳创建一个该用户的session
        new_session = md5(student_email + str(int(time.time())))
        sql_registering = """\
        INSERT INTO register (email, password, session) \
        VALUES ('{}', '{}', '{}');\
        """.format(student_email, student_pwd, new_session)
        fb_registering = database.execute(sql_registering)

        if fb_registering == False:     # 数据库错误
            resp = Response(json.dumps({'code':'ALG001', 'msg':'数据库异常'}))
            return resp

        # 预注册成功，返回reg_session并跳转到register页面
        resp = Response(json.dumps({'code':'302', 'msg':'/register/'}))
        resp.set_cookie("reg_session", new_session, max_age=604800, httponly=True)
        return resp

    else:   # 返回Flase
        resp = Response(json.dumps({'code':'ALG001', 'msg':'数据库异常'}))
        return resp
# API LOGIN 结束


# REGISTER 页面开始
@app.route("/register/", methods=['GET',])
def register():
    # 初始化数据库操作
    database = a_sql.database(mysql_config)

    session = request.cookies.get("reg_session")
    # 如果未携带reg_session则跳转到login页面
    if session == None:
        return redirect(url_for("login"))

    sql_check_session = """\
    SELECT email, password FROM register \
    WHERE session='{}' \
    AND TIMESTAMPDIFF(HOUR , session_at, NOW()) < 1;\
    """.format(session)
    fb_check_session = database.execute(sql_check_session)

    if fb_check_session:
        email, password = fb_check_session[0]
        return render_template("register.html", email = email, password = password)
    else:       # 返回Flase或空元组
        return redirect(url_for("login"))
# REGISTER 页面结束


# API REGISTER 开始
@app.route("/api/register/", methods=['POST',])
def api_register():
    # 接收注册数据
        
    img_url = b_decode(request.form.get("img_url"))
    email_address = b_decode(request.form.get("email"))
    veri_code = b_decode(request.form.get("veri_code"))
    nickname = b_decode(request.form.get("nickname"))
    session = request.cookies.get("reg_session")
    password = b_decode(request.form.get("password"))
    if len(img_url) == 0 or len(email_address) == 0 or len(veri_code) == 0 or len(nickname) == 0 or len(password) == 0:
        resp = Response(json.dumps({'code':'ARG002', 'msg':'存在空数据'}))
        return resp
    else:
        veri_code = int(veri_code)


    # 初始化数据库操作
    database = a_sql.database(mysql_config)

    # 检查验证码是否正确，邮箱 昵称 是否重复
    sql_check_email = """\
    SELECT email \
    FROM user \
    WHERE email='{}'\
    """.format(email_address)
    sql_check_vericode = """\
    SELECT veri_code \
    FROM register \
    WHERE session='{}';\
    """.format(session)
    sql_check_nickname = """\
    SELECT name \
    FROM user \
    WHERE name='{}';\
    """.format(nickname)

    fb_check_email_vericode_nickname = database.execute_m([sql_check_email, sql_check_vericode, sql_check_nickname])
    if fb_check_email_vericode_nickname:
        fb_check_email, fb_check_vericode, fb_check_nickname = fb_check_email_vericode_nickname
        if not fb_check_email:
            if fb_check_vericode[0][0] == veri_code:
                if not fb_check_nickname:
                    # 验证通过，开始注册
                    # 删除register中的数据，避免用户成功注册后重复注册
                    sql_delete_register = """\
                    DELETE FROM register \
                    WHERE session = '{}';\
                    """.format(session)
                    database.execute(sql_delete_register)

                    new_session = md5(email_address + str(int(time.time())))
                    sql_register = """\
                    INSERT INTO user (name, password, email, session) \
                    VALUES ('{}', '{}', '{}', '{}');\
                    """.format(nickname, password, email_address, new_session)
                    fb_register = database.execute(sql_register)

                    if fb_register == False:        # 注册失败
                        resp = Response(json.dumps({'code':'ARG005', 'msg':'数据库写入失败'}))
                        return resp
                    else:
                        # 注册成功
                        sql_get_id = """\
                        SELECT id FROM user \
                        WHERE email='{}';\
                        """.format(email_address)
                        fb_get_id = database.execute(sql_get_id)
                        if fb_get_id:
                            user_id = fb_get_id[0][0]
                            user_id = str(user_id)      # 把id转换为string以作为头像名写入文件
                            image = forum_img.image()       # 创建image对象
                            image.save_avatar(img_url, str(user_id))        # 把用户头像写入文件

                            resp = Response(json.dumps({'code':'ARG006', 'msg':'/'}))     # 注册成功，返回主页url
                            resp.set_cookie("session", new_session, 604800, httponly=True)
                            return resp
                        else:
                            resp = Response(json.dumps({'code':'ARG007', 'msg':'注册时出现了错误'}))
                            return resp
                                                
    
                else:
                    resp = Response(json.dumps({'code':'ARG004', 'msg':'该用户名已被占用'}))
                    return resp
            else:
                resp = Response(json.dumps({'code':'ARG003', 'msg':'邮箱验证码错误'}))
                return resp
        else:
            resp = Response(json.dumps({'code':'ARG001', 'msg':'该邮箱已被注册'}))
            return resp

    else:
        resp = Response(json.dumps({'code':'ARG008', 'msg':'数据库发送了一个错误'}))
        return resp

# API REGISTER 结束


# API REGISTER/GET VERI-CODE 开始
@app.route("/api/register/vericode", methods=['POST',])
def apt_register_vericode():
    student_email = request.form.get("email")
    session = request.cookies.get("reg_session")
    vericode = random.randint(111111, 999999)
        
    # 初始化数据库操作
    database = a_sql.database(mysql_config)

    sql_set_vericode = """\
    UPDATE register \
    SET veri_code = {} \
    WHERE session = '{}';\
    """.format(vericode, session)
    database.execute(sql_set_vericode)
    
    send_code = a_email.email(email_config)
    send_code.send([student_email,], "论坛注册验证码", "你的注册验证码是: {}".format(vericode))
    return "{'code':'ARV001', 'msg':'验证码已发送至您的邮箱'}"

# API REGISTER/GET VERI-CODE 开始



# HOME 页面开始
@app.route("/", methods=['GET',])
def home():
    # 初始化数据库操作
    database = a_sql.database(mysql_config)

    # 头部信息处理
    logined = 0
    notice_num = 0
    user_id = 0
    session = request.cookies.get("session")
    if session:
        sql_get_user = """\
        SELECT id \
        FROM user \
        WHERE session = '{}' \
        AND TIMESTAMPDIFF(HOUR , session_at, NOW()) < 7;\
        """.format(session)
        fb_get_user = database.execute(sql_get_user)
        if fb_get_user:     # 该session有效，并赋值给id和name
            user_id = fb_get_user[0][0]
            logined = 1
            # 获取未读通知数
            sql_get_notification = """\
            SELECT COUNT(to_user) \
            FROM notification \
            WHERE to_user = {} \
            AND seen = 0;\
            """.format(user_id)
            fb_get_notification = database.execute(sql_get_notification)
            notice_num = fb_get_notification[0][0]
     
    # 用户未登录,返回默认头部信息====================

    # 采集帖子并整理
    posts_data = ""     # 存放所有取到帖子的数据
    # 获取对应信息，按最新回复时间排序，一次取30条
    sql_get_posts = """\
    SELECT post.id, post.poster_id, s1.name, post.title, post.last_replyer, s2.name, post.last_reply_at, post.reply_num, top \
    FROM post \
    INNER JOIN user AS s1 ON poster_id = s1.id \
    INNER JOIN user AS s2 ON last_replyer = s2.id \
    ORDER BY last_reply_at DESC;\
    """

    fb_get_posts = database.execute(sql_get_posts)
    
    # 取回信息,对信息进行整理
    for post in fb_get_posts:
        # sql_id_to_nickname = "SELECT name FROM user WHERE id={}"
        post_id, poster_id, poster_nickname, title, last_reply_id, last_replyer_nickname, last_reply_at, reply_num, top = post
        post_data = """\
        post_id: {0}, poster_nickname: '{1}', poster_id: {2}, title: '{3}', \
        last_reply_at: '{4}', last_replyer_nickname: '{5}', last_replyer_id: {6}, \
        reply_num: {7}, top: {8}\
        """.format(post_id, poster_nickname, poster_id, title, last_reply_at, last_replyer_nickname, last_reply_id, reply_num, top )
        post_data = '{' + post_data + '},'
        posts_data = posts_data + post_data
    # 整理信息完毕

    resp = Response(render_template("home.html", login=logined, notice_num=notice_num, user_id=user_id, posts_data=posts_data))
    if logined == 0:    # 未登录或失效的session，删除该cookie，防止下次再收到无效session
        resp.set_cookie("session", "", 0, httponly=True)
    return resp
# HOME 页面结束


# POST 页面开始
@app.route("/post/<int:inquiry_post_id>/", methods=['GET',])
def post(inquiry_post_id):
    database = a_sql.database(mysql_config)

    # 头部信息处理
    logined = 0
    notice_num = 0
    user_id = 0
    session = request.cookies.get("session")
    if session:
        sql_get_user = """\
        SELECT id \
        FROM user \
        WHERE session = '{}' \
        AND TIMESTAMPDIFF(HOUR , session_at, NOW()) < 7;\
        """.format(session)
        fb_get_user = database.execute(sql_get_user)
        if fb_get_user:     # 该session有效，并赋值给id和name
            user_id = fb_get_user[0][0]
            logined = 1
            # 获取未读通知数
            sql_get_notification = """\
            SELECT COUNT(to_user) \
            FROM notification \
            WHERE to_user = {} \
            AND seen = 0;\
            """.format(user_id)
            fb_get_notification = database.execute(sql_get_notification)
            notice_num = fb_get_notification[0][0]

    # 用户未登录,返回默认头部信息====================

    # 更新帖子的点击量加1
    sql_update_clickNum = """\
    UPDATE post \
    SET click_num = click_num + 1 \
    WHERE id = {};\
    """.format(inquiry_post_id)
    # database.execute(sql_update_clickNum)
    # 获取帖子相关信息
    sql_get_post = """\
    SELECT post.id, posted_at, click_num, title, content, poster_id, user.name \
    FROM post INNER JOIN user \
    ON poster_id = user.id \
    WHERE post.id = {};\
    """.format(inquiry_post_id)
    # fb_get_post = database.execute(sql_get_post)
    
    # 获取回复内容
    sql_get_reply = """\
    SELECT replyer, user.name, reply_at, content, id_inside \
    FROM reply \
    INNER JOIN user \
    WHERE replyer = user.id \
    AND post_id = {} \
    ORDER BY id_inside;\
    """.format(inquiry_post_id)
    # fb_get_reply = database.execute(sql_get_reply)

    fb_get_post_reply = database.execute_m([sql_update_clickNum, sql_get_post, sql_get_reply])
    if fb_get_post_reply:
        _, fb_get_post, fb_get_reply = fb_get_post_reply
        if fb_get_post:        # 成功获取到帖子相关信息

            # 整理info内容
            reply_num = len(fb_get_reply)
            info = "{}条回复 {}".format(str(reply_num), time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            # 整理回复内容
            all_reply = ""
            for reply in fb_get_reply:
                replyerID, replyerName, replyTime, replyContent, floor = reply
                single_reply = """\
                'replyerID':{}, 'replyerName':'{}', 'replyTime':'{}', \
                'replyContent':'{}', 'floor':'{}'\
                """.format(replyerID, replyerName, replyTime, replyContent, floor)
                single_reply = '{' + single_reply + '},'
                all_reply += single_reply

            # 整理帖子主题
            post_id, posted_time, click_num, topic, content, hoster_id, hoster_name = fb_get_post[0]
            host = """\
            'hosterID':{0}, 'hosterName':'{1}', 'postID':'{2}', 'postedTime':'{3}', \
            'clickNum':'{4}', 'topic':'{5}', 'content':'{6}'\
            """.format(hoster_id, hoster_name, post_id, posted_time, click_num, topic, content)
            host = '{' + host + '},'

        else:
            # 获取帖子失败,跳转到404页面(还没写，用主页代替)
            resp = Response(redirect(url_for('home')))
            return resp

        resp = Response(render_template('post.html', host_data=host, reply_data=all_reply, info=info, login=logined, notice_num=notice_num, user_id=user_id))
        if logined == 0:    # 未登录或失效的session，删除该cookie，防止下次再收到无效session
            resp.set_cookie("session", "", 0, httponly=True)
        return resp
    else:
        # 数据库处理错误，跳转到404页面(还没写，用主页代替)
        resp = Response(redirect(url_for('home')))
        return resp
# POST 页面结束


# 发送回复
@app.route("/api/reply/", methods=['POST',])
def api_reply():
    session = request.cookies.get("session")
    post_id = request.form.get("postID")
    reply_content = request.form.get("replyContent")


    if len(reply_content) == 0:
        resp = Response(json.dumps({'code':'ARP001', 'msg':'无效的内容'}))
        return resp
    
    # 初始化数据库
    database = a_sql.database(mysql_config)
    # 获取用户ID
    sql_get_userID = """\
    SELECT id \
    FROM user \
    WHERE session = '{}' \
    AND TIMESTAMPDIFF(DAY, session_at, NOW()) < 7;\
    """.format(session)
    fb_get_userID = database.execute(sql_get_userID)

    if fb_get_userID:
        user_id = fb_get_userID[0][0]
        # 插入数据
        sql_send_reply = """\
        INSERT INTO reply (post_id, id_inside, replyer, content) \
        VALUES ({0}, \
        (SELECT COUNT(id) FROM (SELECT id FROM reply WHERE post_id = {1}) AS temp)+1, {2}, '{3}');\
        """.format(post_id, post_id, user_id, reply_content)
        
        # 更新post表
        sql_update_last_replyer = """\
        UPDATE post \
        SET last_replyer = {}, last_reply_at = '{}' \
        WHERE id = {}\
        """.format(user_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), post_id)

        fb_insert_reply = database.execute_m([sql_send_reply, sql_update_last_replyer])
        if fb_insert_reply:
            resp = Response(json.dumps({'code':'ARP004', 'msg':'/post/' + post_id + '/'}))
            return resp
        else:
            resp = Response(json.dumps({'code':'ARP003', 'msg':'回复失败'}))
            return resp
    else:
        resp = Response(json.dumps({'code':'ARP002', 'msg':'未登录或该session已失效'}))
        return resp
    
    
    
# 发送回复 结束

# 上传头像 开始 
@app.route("/api/upload/avatar/", methods=['POST',])
def upload():
    avatar_name = str(int(time.time())) + "_" + str(random.randint(0, 1000))
    avatar_location = project_location + "static\\images\\temp\\{}.png".format(avatar_name)
    file = request.files['photo']
    file.save(avatar_location)

    # 创建image对象
    image = forum_img.image()
    image_name = image.save_file(avatar_location)
    resp = Response(json.dumps({'code':'AUA001', 'msg':'{}'.format("/static/images/temp/" + image_name + ".png")}))
    return resp
# 上传头像 结束

# posting 页面开始
@app.route("/posting/", methods=['GET',])
def posting():
    # 初始化数据库
    database = a_sql.database(mysql_config)

    # 头部信息处理
    logined = 0
    notice_num = 0
    user_id = 0
    session = request.cookies.get("session")
    if session:
        sql_get_user = """\
        SELECT id \
        FROM user \
        WHERE session = '{}' \
        AND TIMESTAMPDIFF(HOUR , session_at, NOW()) < 7;\
        """.format(session)
        fb_get_user = database.execute(sql_get_user)
        if fb_get_user:     # 该session有效，并赋值给id和name
            user_id = fb_get_user[0][0]
            logined = 1
            # 获取未读通知数
            sql_get_notification = """\
            SELECT COUNT(to_user) \
            FROM notification \
            WHERE to_user = {} \
            AND seen = 0;\
            """.format(user_id)
            fb_get_notification = database.execute(sql_get_notification)
            notice_num = fb_get_notification[0][0]
    # 用户未登录,返回默认头部信息====================

    resp = Response(render_template("posting.html", login=logined, notice_num=notice_num, user_id=user_id))
    if logined == 0:    # 未登录或失效的session，删除该cookie
        resp.set_cookie("session", "", 0, httponly=True)
    return resp
# posting页面结束

# 发送post 开始
@app.route("/api/posting/", methods=['POST',])
def api_posting():
    session = request.cookies.get("session")
    title = request.form.get("title")
    content = request.form.get("content")

    if len(title) == 0:
        resp = Response(json.dumps({'code':'APT001', 'msg':'标题不允许为空'}))
        return resp
    
    # 初始化数据库
    database = a_sql.database(mysql_config)
    # 获取用户ID
    sql_get_userID = """\
    SELECT id \
    FROM user \
    WHERE session = '{}' \
    AND TIMESTAMPDIFF(DAY, session_at, NOW()) < 7;\
    """.format(session)
    fb_get_userID = database.execute(sql_get_userID)
    if fb_get_userID:
        user_id = fb_get_userID[0][0]
    else:
        resp = Response(json.dumps({'code':'APT002', 'msg':'未登录或该session已失效'}))
        return resp
    
    # 插入帖子
    sql_insert_post = """\
    INSERT INTO post (poster_id, title, content, last_replyer) \
    VALUES ({}, '{}', '{}', {});\
    """.format(user_id, title, content, user_id)

    fb_insert_post = database.execute(sql_insert_post)

    if fb_insert_post == False:
        resp = Response(json.dumps({'code':'APT003', 'msg':'发布失败'}))
        return resp
    else:
        # 获取新发布帖子的ID
        sql_get_postID = """\
        SELECT id \
        FROM post \
        WHERE poster_id = {} \
        ORDER BY last_reply_at DESC \
        LIMIT 1;\
        """.format(user_id)
        fb_get_postID = database.execute(sql_get_postID)[0][0]
        # 发布帖子成功
        resp = Response(json.dumps({'code':'APT004', 'msg':'/post/' + str(fb_get_postID) + '/'}))
        return resp
# 发布帖子 结束
    

# 该函数用于接收一串字符串并返回base64
def b_encode(sentence):
    if sentence is None:
        return ""
    return base64.b64encode(sentence.encode("UTF-8"))
# 结束


# 该函数用于接收一串base64并返回字符串
def b_decode(sentence):
    if sentence is None:
        return ""
    return base64.b64decode(sentence).decode('UTF-8')
# 结束


# 该函数用于接收一串字符串并返回md5
def md5(sentence):
    m = hashlib.md5()
    m.update(sentence.encode())
    return m.hexdigest()
# 结束




if __name__ == "__main__":
    # 读配置文件
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Mysql Part
    mysql_host = config['mysql']['host']
    mysql_user = config['mysql']['user']
    mysql_password = config['mysql']['password']
    mysql_database = config['mysql']['database']
    mysql_charset = config['mysql']['charset']
    mysql_config = [mysql_host, mysql_user, mysql_password, mysql_database, mysql_charset]

    # Email Part
    email_sender = config['email']['sender']
    email_username = config['email']['username']
    email_password = config['email']['password']
    email_config = [email_sender, email_username, email_password]

    # Server Part
    server_host = config['server']['host']
    server_port = config['server']['port']

    # 启动服务
    app.run(host=server_host, port=server_port, debug=True)


