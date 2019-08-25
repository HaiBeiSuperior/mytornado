from .base import BaseHandler
from .models import User,Category,Goods,GoodsImg,Coupons,Order,OrderDetail,Comments
from db import sess,AlchemyEncoder
import re,json,os,jwt
from sqlalchemy import func
from func_tool import set_storage,get_storage,get_ali_object,get_order_code,api_alipay_trade_refund
import redis,requests
from Decorator import decorator
from settings import jwt_code
from sqlalchemy import and_

# sess.query(Goods.gname,Goods.id,Goods.price,GoodsImg.image).join(GoodsImg,GoodsImg.goods_id==Goods.id).all()

def infinite(goodsList,id,num,start):
    # 获取该分类下所有商品
    good = sess.query(Goods.gname,Goods.id,Goods.price,GoodsImg.image,GoodsImg.img_order,Goods.describe).join(GoodsImg,GoodsImg.goods_id==Goods.id).filter(and_(Goods.cate_id == id,GoodsImg.img_order==1)).limit(num).offset(start).all()
    cate2 = sess.query(Category).filter(Category.parent_id == id).all()
    for i in good:
        goodsList.append(i)
    if len(cate2) == 0:
        pass
    else:
        for j in cate2:
            infinite(goodsList,j.id,num,start)

class Index(BaseHandler):
    def post(self, *args, **kwargs):
        mes = {}
        cur = int(self.get_argument('cur',1)) # 当前页
        num = int(self.get_argument('num'))        # 每页数量
        cateList = sess.query(Category).filter(Category.parent_id == 0).all()
        goods = sess.query(Goods).all()
        totalNum = len(goods)
        start = (cur-1)*num
        goodsList = sess.query(Goods.gname,Goods.id,Goods.price,GoodsImg.image,GoodsImg.img_order,Goods.describe).join(GoodsImg,GoodsImg.goods_id==Goods.id).filter(GoodsImg.img_order==1).limit(num).offset(start).all()
        print(goodsList)
        mes['cateList'] = cateList
        mes['goodsList'] = goodsList
        mes['count'] = totalNum
        mes['code'] = 200
        mes['message'] = '发送成功'
        self.write(json.dumps(mes,cls=AlchemyEncoder,ensure_ascii=False,indent=4))

class GetGoodss(BaseHandler):
    def post(self, *args, **kwargs):
        mes = {}
        id = self.get_argument('id')
        cur = int(self.get_argument('cur', 1))  # 当前页
        num = int(self.get_argument('num'))  # 每页数量
        goods = sess.query(Goods).filter(Goods.cate_id==id).all()
        print(id,'0-0-0-0-0-0-0')
        totalNum = len(goods)
        start = (cur - 1) * num
        goodsList = []
        infinite(goodsList,id,num,start)
        mes['goods_list'] = goodsList
        mes['count'] = totalNum
        mes['code'] = 200
        mes['message'] = '发送分类成功'
        self.write(json.dumps(mes,cls=AlchemyEncoder,ensure_ascii=False,indent=4))


# sess.query(Goods.gname,Goods.id,Goods.price,GoodsImg.image).join(GoodsImg,GoodsImg.goods_id==Goods.id).all()
class GetGoods(BaseHandler):
    def get(self, *args, **kwargs):
        mes = {}
        id = self.get_argument('id')
        goods = sess.query(Goods.gname,Goods.id,Goods.price,GoodsImg.image).join(GoodsImg,GoodsImg.goods_id==Goods.id).filter(Goods.id == id).first()

        img = sess.query(GoodsImg).filter(GoodsImg.goods_id == id).all()
        mes['img'] = img
        mes['goods'] = goods
        mes['code'] = 200
        mes['message'] = '发送分类成功'


        self.write(json.dumps(mes,cls=AlchemyEncoder,ensure_ascii=False,indent=4))

# 前端购物车数据存储到Redis中
class StorageRedis(BaseHandler):
    @decorator
    def post(self, *args, **kwargs):
        conn = redis.Redis(host="localhost", port=6379)
        cartList = self.get_argument('cart')
        token = self.get_argument('token')
        u_name = self.get_argument('u_name')

        conn.set(u_name,cartList)

# 获取用户id
class TreeHandler(BaseHandler):
    async def get(self):

        ip = self.request.remote_ip
        conn = redis.Redis(host="localhost", port=6379)
        conn.sadd('ip',ip)
        val = conn.scard('ip')
        mes = {
            'total_user':val,
            'code':200,
        }
        self.write(json.dumps(mes, cls=AlchemyEncoder, ensure_ascii=False, indent=4))


# header页发送关键字搜索/模糊查询
class SearchContent(BaseHandler):
    async def get(self):
        mes = {}
        content = self.get_argument("c")
        goodsList = sess.query(Goods.gname,Goods.id,Goods.price,GoodsImg.image,GoodsImg.img_order,Goods.describe)\
            .join(GoodsImg,GoodsImg.goods_id==Goods.id)\
            .filter(Goods.gname.like("%"+content+"%")).all()
        mes['code'] = 200
        mes['goodsList'] = goodsList
        self.write(json.dumps(mes, cls=AlchemyEncoder, ensure_ascii=False, indent=4))


# 获取优惠券code码并将优惠券所有信息返回前端
class GetCoupons(BaseHandler):
    @decorator
    async def post(self):
        mes = {}
        code = self.get_argument('code')
        coupons = sess.query(Coupons).filter(Coupons.code == code).first()
        if coupons:
            mes['discount'] = float(coupons.discount)
            mes['code'] = 200
        else:
            pass
        self.write(json.dumps(mes,cls=AlchemyEncoder,ensure_ascii=False,indent=4))




class PayPageHandler(BaseHandler):

    # @decorator
    async def post(self):

        # 根据当前用户的配置，生成URL，并跳转。
        cartString = self.get_argument('cartList')
        code = self.get_argument('code','')
        u_name = self.get_argument('u_name')
        cartList = json.loads(cartString)
        order_code = str(get_order_code())
        address = '北京'
        totalPrice = 0
        goodslist = []
        for i in cartList:
            print(i)

            goods = sess.query(Goods).filter(Goods.id == i['id']).first()
            totalPrice += goods.price * i['num']
            dict_ = {
                'gname': i['name'],
                'price': i['price'],
                'num': i['num'],
                'total': goods.price * i['num']
            }
            goodslist.append(dict_)
        user = sess.query(User).filter(User.username==u_name).first()
        goodslist = json.dumps(goodslist,ensure_ascii=False)
        coupons = sess.query(Coupons).filter(Coupons.code == code).first()
        if code == '':
            money = totalPrice

            order = Order(
                id=order_code,ststes=0,order_amount=totalPrice,payment_amount=money,user_id=user.id
            )

            try:
                sess.add(order)
                sess.commit()
            except:
                pass

            alipay = get_ali_object()

            # 生成支付的url
            query_params = alipay.direct_pay(
                subject="test",  # 商品简单描述
                out_trade_no=order_code,  # 用户购买的商品订单号（每次不一样） 20180301073422891
                total_amount=money,  # 交易金额(单位: 元 保留俩位小数)
            )

            pay_url = "https://openapi.alipaydev.com/gateway.do?{0}".format(query_params)  # 支付宝网关地址（沙箱应用）

        else:

            money = round(totalPrice * coupons.discount)
            order = Order(
                id=order_code, ststes=0, order_amount=totalPrice, payment_amount=money,user_id=user.id
            )
            sess.add(order)
            sess.commit()
            alipay = get_ali_object()

            # 生成支付的url
            query_params = alipay.direct_pay(
                subject="test",  # 商品简单描述
                out_trade_no=order_code,  # 用户购买的商品订单号（每次不一样） 20180301073422891
                total_amount=money,  # 交易金额(单位: 元 保留俩位小数)
            )

            pay_url = "https://openapi.alipaydev.com/gateway.do?{0}".format(query_params)  # 支付宝网关地址（沙箱应用）

        order_detail = OrderDetail(
            goodslist=goodslist, distribution_amoubt=0, goods_address=address, order_id=order_code
        )

        try:
            sess.add(order_detail)
        except:
            pass
        self.write(json.dumps({'pay_url':pay_url}))

#支付宝回调
class PayRetrunHandler(BaseHandler):
    async def get(self):

        params = self.request.arguments

        procts = params['out_trade_no'][0]
        proct_code = str(procts.decode())

        procts_ = params['trade_no'][0]
        trade_no = str(procts_.decode())

        order = sess.query(Order).filter(Order.id == proct_code).first()
        if order:
            order.outer_traed_number = trade_no
            order.ststes = 1
            sess.commit()

            self.redirect('http://127.0.0.1:8080/checkout?ord={}'.format(order.id))
        else:
            pass

# 获取订单
class GetOrder(BaseHandler):
    def post(self, *args, **kwargs):
        mes = {}
        oid = self.get_argument('o_id')
        if oid:
            orderList = sess.query(Order).filter(Order.id == oid).first()
            mes['code'] = 200
            mes['orderList'] = orderList
            self.write(json.dumps(mes,cls=AlchemyEncoder,ensure_ascii=False,indent=4))



class Refund(BaseHandler):
    def post(self):
        oid = self.get_argument('o_id')
        if oid:
            orderList = sess.query(Order).filter(Order.id == oid).first()
            #调用退款方法
            order_string = api_alipay_trade_refund(
            #订单号，一定要注意，这是支付成功后返回的唯一订单号
            out_trade_no = orderList.id,
            #退款金额，注意精确到分，不要超过订单支付总金额
            refund_amount = orderList.payment_amount,
            #回调网址
            notify_url='http://127.0.0.1:8000/alipayreturn'
            )
            print(order_string)
            orderList.ststes = 2
            orderList.commit()



# 获取当前商品的所有评论
class GrtComments(BaseHandler):
    def post(self):
        # 1. 查询当前商品下的所有评论
        # 通过商品ID查询Comments表中所有评论以及评论的用户
        goods_id = self.get_argument('goods_id')
        print(goods_id,'0-0-0-0-0-0')
        if goods_id:
            comments = sess.query(Comments).filter(Comments.goods_id==goods_id).all()
            print(comments,'-=-=-=-=-=-=-=-=-=')
            self.write(json.dumps({'code':200,'comments':comments},cls=AlchemyEncoder,ensure_ascii=False,indent=4))


# 用户发表评论
class PubComments(BaseHandler):
    async def post(self):
        tinymceHtml = self.get_argument('tinymceHtml')
        goods_id = self.get_argument('goods_id')
        gname = self.get_argument('gname')
        u_name = self.get_argument('u_name')
        # 1. 查询当前用户是否购买过该商品 买过--->可以评论   没买过--->不能评论
        # 通过u_name ---> 查出用户id ---> 查出该用户的所有ststes=1订单（遍历订单获取订单ID） ---> 查询订单详情（获取订单详情字段）
        # ---> 将json数据取出后遍历获取商品ID
        # 判断 如果当前商品ID存在详情中商品ID内，则买过，反之没买过
        # 2. 将发表的评论存到数据库
        # goods = [(json.loads(i[0]))[0]['gname'] for i in sess.query(OrderDetail.goodslist).join(Order,Order.id==OrderDetail.order_id).join(User,User.id==Order.user_id).filter(User.username==u_name).all()]
        goodslist = sess.query(OrderDetail.goodslist,User.id).join(Order,Order.id==OrderDetail.order_id).filter(Order.ststes==1).join(User,User.id==Order.user_id).filter(User.username==u_name).all()
        gList = []
        id = 0
        for i in goodslist:
            goods = json.loads(i[0])
            gname = goods[0]['gname']
            gList.append(gname)
            id = i[-1]
        if gname in gList:
            comments = Comments(content=tinymceHtml,user_id=id,goods_id=goods_id)
            sess.add(comments)
            sess.commit()
            self.write(json.dumps({'code': 200, 'mes': '评论成功'}))
        else:
            self.write(json.dumps({'code':100022,'mes':'没有购买过该商品'}))


