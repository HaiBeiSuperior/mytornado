from func_tool import SmsValidation,set_storage,get_storage,sendmail
from .base import BaseHandler
from .models import User
from db import sess
import re,json,requests,settings
import random,jwt,sys

from celery import Celery
from tornado import gen
import tcelery
sys.path.append("..")
import task

#异步任务
class CeleryHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        response = yield gen.Task(task.mail.apply_async,args=['你好','非常好','164850527@qq.com'])
        self.write('ok')
        self.finish()



class UserLogin(BaseHandler):
    def post(self, *args, **kwargs):
        mes = {}
        u_name = self.get_argument('u_name')
        pwd = self.get_argument('pwd')
        if not all([u_name,pwd]):
            mes['code'] = 400
            mes['message'] = '请输入账号密码'
            self.write(json.dumps(mes))
        else:
            user = sess.query(User).filter(User.username == u_name).first()
            if user is not None:
                if user.password != pwd:
                    mes['code'] = 400
                    mes['message'] = '密码错误'
                    self.write(json.dumps(mes))
                else:
                    encoded_jwt = jwt.encode({'u_name': user.username},settings.jwt_code, algorithm='HS256')
                    mes['code'] = 200
                    mes['token'] = str(encoded_jwt,'utf-8')
                    mes['message'] = '登录成功'
                    self.write(json.dumps(mes))
            else:
                mes['code'] = 400
                mes['message'] = '该账号不存在'
                self.write(json.dumps(mes))




class UserRegister(BaseHandler):
    def post(self, *args, **kwargs):
        mes = {}
        username = self.get_argument('username')
        pwd1 = self.get_argument('pwd1')
        pwd2 = self.get_argument('pwd2')
        nick = self.get_argument('nick')
        code = self.get_argument('code')
        email = self.get_argument('email')
        phone = self.get_argument('phone')
        if not all([username,pwd1,pwd2,phone]):
            mes['code'] = 400
            mes['message'] = '请填写全部信息'
            self.write(json.dumps(mes))
        else:
            if len(username) <6 or len(username) > 12:
                mes['code'] = 400
                mes['message'] = '请输入6-12位用户名'
                self.write(json.dumps(mes))
            elif re.match('\w{6,12}$',username) == None:
                mes['code'] = 400
                mes['message'] = '用户名不能使用特殊符号'
                self.write(json.dumps(mes))
            elif sess.query(User).filter(User.username == username).first():
                mes['code'] = 400
                mes['message'] = '用户名已存在'
                self.write(json.dumps(mes))
            elif re.match('\w{4,20}@(qq|126|163|gmail)(.com)$',email) == None:
                mes['code'] = 400
                mes['message'] = '请正确填写邮箱'
                self.write(json.dumps(mes))
            elif re.match('^1[35789]\d{9}$',phone) == None:
                mes['code'] = 400
                mes['message'] = '请正确填写手机号码'
                self.write(json.dumps(mes))
            elif sess.query(User).filter(User.phone == phone).first():
                mes['code'] = 400
                mes['message'] = '该手机已被占用'
                self.write(json.dumps(mes))
            elif pwd1 != pwd2:
                mes['code'] = 400
                mes['message'] = '两次密码不一致'
                self.write(json.dumps(mes))
            elif code is None:
                mes['code'] = 400
                mes['message'] = '请输入验证码'
                self.write(json.dumps(mes))
            else:
                if get_storage(phone):
                    _code = get_storage(phone).decode()
                    if _code != code:
                        mes['code'] = 400
                        mes['message'] = '验证码错误'
                        self.write(json.dumps(mes))
                    else:
                        user = User(username=username,password=pwd1,nick=nick,phone=phone,email=email)
                        try:
                            sess.add(user)
                        except:
                            mes['code'] = 400
                            mes['message'] = '连接服务器超时请重新注册'
                            self.write(json.dumps(mes))
                        ret = sendmail(email,nick)
                        if ret:
                            encoded_jwt = jwt.encode({'u_name': user.username}, settings.jwt_code, algorithm='HS256')
                            user_ = sess.query(User).filter(User.phone == phone).first()
                            mes['token'] = str(encoded_jwt, 'utf-8')
                            mes['activation_code'] = 200
                            mes['username'] = user_.username
                            mes['code'] = 200
                            mes['message'] = 'ok'
                            self.write(json.dumps(mes))
                        else:
                            encoded_jwt = jwt.encode({'u_name': user.username}, settings.jwt_code, algorithm='HS256')
                            user_ = sess.query(User).filter(User.phone == phone).first()
                            mes['token'] = str(encoded_jwt, 'utf-8')
                            mes['activation_code'] = 300
                            mes['username'] = user_.username
                            mes['code'] = 200
                            mes['message'] = 'ok'
                            self.write(json.dumps(mes))
                else:
                    mes['code'] = 400
                    mes['message'] = '验证码错误'
                    self.write(json.dumps(mes))





class GetCode(BaseHandler):
    def post(self, *args, **kwargs):
        mes = {}
        phone = self.get_argument('phone')
        if phone is not None:
            validation = str(random.randrange(0, 10000))
            SmsValidation(phone, validation)
            set_storage(phone,validation)
            mes['code'] = 200
            mes['message'] = 'ok'
            self.write(json.dumps(mes))
        else:
            mes['code'] = 400
            mes['message'] = '请输入正确的手机号码'
            self.write(json.dumps(mes))

class Send(BaseHandler):
    def post(self, *args, **kwargs):
        mes = {}
        user_id = self.get_argument('user_id')
        if user_id is not None:
            user = sess.query(User).filter(User.id == user_id).first()
            user.is_activates = 1
            mes['code'] = 200
            mes['message'] = '激活成功'
            self.write(json.dumps(mes))
        else:
            mes['code'] = 400
            mes['message'] = '请求错误'
            self.write(json.dumps(mes))

# 微博登陆--请求拼接url
class SinaFirstHandler(BaseHandler):

    def get(self,*args,**kwargs):
        mes = {}
        # 微博接口地址
        weibo_auth_url = "https://api.weibo.com/oauth2/authorize"
        # 回调网址
        redirect_url = "http://127.0.0.1:8000/md_admin/weibo"
        # 应用id
        client_id = "2636039333"
        # 组合url
        auth_url = weibo_auth_url + "?client_id={client_id}&redirect_uri={re_url}".format(client_id=client_id,
                                                                                          re_url=redirect_url)
        # self.write(json.dumps({'code':200,'auth_url':auth_url}))
        mes['auth_url'] = auth_url
        mes['code'] = 200
        mes['mess'] = '成功'
        self.write(json.dumps(mes, indent=4, ensure_ascii=False))

# 微博登陆成功后回调
class SinaBackHandler(BaseHandler):

    def get(self,*args,**kwargs):
        # 获取回调的code
        code = self.get_argument('code')
        # 微博认证地址
        access_token_url = "https://api.weibo.com/oauth2/access_token"
        # 参数 向新浪接口发送请求
        re_dict = requests.post(access_token_url, data={
            "client_id": '2636039333',
            "client_secret": "4e2fbdb39432c31dc5c2f90be3afa5ce",
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://127.0.0.1:8000/md_admin/weibo",
        })

        re_dict = re_dict.text
        re_dict = eval(re_dict)
        uid = str(re_dict.get('uid'))
        if uid:
            # nick = '新浪微博登录的'+uid
            _user = sess.query(User).filter(User.username == uid).first()
            encoded_jwt = jwt.encode({'u_name': _user.username}, settings.jwt_code, algorithm='HS256')
            token = str(encoded_jwt, 'utf-8')
            if _user:
                self.redirect('http://127.0.0.1:8080/?u_name={}token={}'.format(_user.username,token))
            else:
                user = User(username=uid,password=settings.PASSWORD,nick=uid,phone='',attributes=1)
                encoded_jwt = jwt.encode({'u_name': user.username}, settings.jwt_code, algorithm='HS256')
                token = str(encoded_jwt,'utf-8')
                try:
                    sess.add(user)
                    _user = sess.query(User).filter(User.username == uid).first()
                    self.redirect('http://127.0.0.1:8080/?u_name={}token={}'.format(_user.username,token))

                except:
                    pass
        else:
            # self.write(re_dict)
            self.redirect('http://127.0.0.1:8080/login')






#获取code url
class Get_authorization_code(BaseHandler):
    def get(self, *args, **kwargs):
        url = 'https://graph.qq.com/oauth2.0/authorize'
        data = {
            'response_type':'code',
            'client_id':'101487535',
            'redirect_uri':'http://login.yskj599.com/user/login/qq_login',
            'state':'101487535'
        }
        con = requests.get(url=url,params=data)
        urls = con.url
        data = {
            'url':urls
        }
        self.write(json.dumps(data))

#QQ登录获取access_token
def QQ_get_access_token(code,app_id):
    app = {
        'grant_type': 'authorization_code',
        'client_id': app_id,
        'client_secret': '9c383c0a358b3382ed52269ccff3691f',
        'code': code,
        'redirect_uri': 'http://login.yskj599.com/user/login'
    }
    access_url = 'https://graph.qq.com/oauth2.0/token'
    response = requests.get(url=access_url, params=app)
    print(response.text)
    print('----------------------------------print(response.text)------------------------------------------------------')
    alist = response.text.split('=')
    access_token = alist[1].split('&')[0]
    refresh_token = alist[3]
    return access_token


#QQ登录获取OpenID
def QQ_get_OpenID(access_token):
    OpenID_url = 'https://graph.qq.com/oauth2.0/me'
    response = requests.get(OpenID_url, params={'access_token': access_token})
    print(response.text)
    print('---------------------------------------------------response = requests.get(OpenID_url, params=: access_token)------------------------------------------------------------------')
    OpenID = response.text.split('"')[-2]
    return OpenID

#QQ登录接口
class QQ_login(BaseHandler):
    def get(self, *args, **kwargs):
        params = self.request.arguments
        app_id = '101487535'
        print(params,'0-0-0-0-0-0-0')
        try:
            code = params['code'][0].decode()
            access_token = QQ_get_access_token(code,app_id)
            OpenID = QQ_get_OpenID(access_token)
            params2 = {
                'access_token':access_token,
                'oauth_consumer_key':'101487535',
                'openid':OpenID
            }
            # QQ返回登录用户的信息
            get_info_url = 'https://graph.qq.com/user/get_user_info'
            response = requests.get(url = get_info_url,params=params2)
            user_info = response.json()
            nickname = user_info['nickname']
            user = sess.query(User).filter(User.nick == nickname).first()
            # encoded_jwt = jwt.encode({'u_name': user.nick}, settings.jwt_code, algorithm='HS256')
            # token = str(encoded_jwt, 'utf-8')
            if user:
                self.redirect('http://127.0.0.1:8080?u_name={}'.format(nickname))
            else:
                qq_user = User(nick = nickname,password = '123456',gender=1,
                               addres =user_info['province'] + user_info['city'],attributes = 2,is_activates = 1)
                sess.add(qq_user)
                sess.commit()
                self.redirect('http://127.0.0.1:8080?u_name={}'.format(nickname))
        except:
            self.write('登录失败')













