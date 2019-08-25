#导包 导入客户端
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import redis,os
import settings
from pay import AliPay
import time
import requests





def SmsValidation(phone,validation):
    #定义短信sid
    account_sid = 'AC9062261b0f2b0b08dac848f392c13f2e'
    #定义秘钥
    auth_token = '1a948ad3558a80b406499efc83e39f55'

    #定义客户端对象
    client = Client(account_sid,auth_token)


    message = client.messages.create(
        to="+86"+phone,     # 接受短信的手机号，也就是注册界面验证过的那个自己的手机号，注意 写中国区号  +86
        from_="+13342471060",   # 发送短信的美国手机号  区号 +1
        body="欢迎登录，本次验证码为："+validation)
    return message


def set_storage(phone,code):
    conn = redis.Redis(host="localhost", port=6379)
    conn.set(phone,code,ex=60) # ex代表seconds，px代表ms


def get_storage(phone):
    conn = redis.Redis(host="localhost", port=6379)
    val = conn.get(phone)
    return val


def sendmail(email,nick):
    ret=True
    try:
        msg=MIMEText(settings.content,'plain','utf-8')
        msg['From']=formataddr([settings.company,settings.my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To']=formataddr([nick,email])              # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = settings.MergeTheme                # 邮件的主题，也可以说是标题

        server=smtplib.SMTP_SSL(settings.SMTP, settings.PORT)  # 发件人邮箱中的SMTP服务器，端口是465
        server.login(settings.my_sender, settings.my_pass)  # smtp秘钥
        server.sendmail(settings.my_sender,[email,],msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()# 关闭连接
    except Exception:# 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret=False
    return ret


# 初始化阿里支付对象
def get_ali_object():
    # 沙箱环境地址：https://openhome.alipay.com/platform/appDaily.htm?tab=info
    app_id = "2016100100640904"  # APPID （沙箱应用）

    # 支付完成后，支付偷偷向这里地址发送一个post请求，识别公网IP,如果是 192.168.20.13局域网IP ,支付宝找不到，def page2() 接收不到这个请求
    notify_url = "http://localhost:80/alipayreturn"

    # 支付完成后，跳转的地址。
    return_url = "http://localhost:80/alipayreturn"

    # 秘钥地址
    key_path = os.path.dirname(os.path.dirname(__file__)) + "/mytornado/keys/"

    merchant_private_key_path = key_path + "app_private_2048.txt"  # 应用私钥
    alipay_public_key_path = key_path + "alipay_public_2048.txt"  # 支付宝公钥

    alipay = AliPay(
        appid=app_id,
        app_notify_url=notify_url,
        return_url=return_url,
        app_private_key_path=merchant_private_key_path,
        alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
        debug=True,  # 默认False,
    )
    return alipay

#支付宝#根据日期生成唯一订单号
def get_order_code():
    order_no = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
    return order_no




#请求支付宝退款接口
def api_alipay_trade_refund(refund_amount, out_trade_no=None, trade_no=None, **kwargs):
    biz_content = {
        "refund_amount": refund_amount
    }
    biz_content.update(**kwargs)
    if out_trade_no:
        biz_content["out_trade_no"] = out_trade_no
    if trade_no:
        biz_content["trade_no"] = trade_no
    alipay = get_ali_object()
    data = alipay.build_body("alipay.trade.refund", biz_content)
    url = "https://openapi.alipaydev.com/gateway.do" + "?" + alipay.sign_data(data)
    r = requests.get(url)
    html = r.content.decode("utf-8")
    return html
