from db import Base
from sqlalchemy import Column,String,Integer,Text,DateTime,ForeignKey,DECIMAL # 内置的创建类的方法属性
from sqlalchemy.orm import relationship,backref
import datetime

# 节点表
class Nodes(Base):
    __tablename__ = 'nodes'
    id = Column(Integer,primary_key=True)
    nname = Column(String(30),unique=True)
    node_url = Column(String(255))

# 角色表
class Roles(Base):
    __tablename__ = 'roles'
    id = Column(Integer,primary_key=True)
    rname = Column(String(30),unique=True)
    node = relationship('Nodes',secondary='role2node',backref=backref('role'))

# 角色、节点多对多关系的中间表
class Role2Node(Base):
    __tablename__ = 'role2node'
    id = Column(Integer,primary_key=True)
    node_id = Column(Integer,ForeignKey('nodes.id'))
    role_id = Column(Integer,ForeignKey('roles.id'))




# 自定义类型
class User(Base):
    # 指定关联数据表
    __tablename__ ='user'
    # 定义属性
    id=Column(Integer,primary_key=True)
    username = Column(String(30))
    password = Column(String(255))
    nick = Column(String(30))
    phone = Column(String(11))
    gender = Column(Integer,default=0)
    email = Column(String(30),default='')
    addres = Column(String(100),default='')
    attributes = Column(Integer,default=0)    # 社交属性 1：微博登录
    is_activates = Column(Integer,default=0)  # 是否激活 1是  0否
    role_id = Column(Integer, ForeignKey('roles.id'))
    role = relationship('Roles', backref=backref('user'))
    # 注意：自定义的类型必须制定关联的数据库表和表中的主键，否则报错。


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer,primary_key=True)
    create_time = Column(DateTime, default=datetime.datetime.now)
    cname = Column(String(50))
    parent_id = Column(Integer,default=0)


class Goods(Base):
    __tablename__ = 'goods'
    id = Column(Integer,primary_key=True)
    gname = Column(String(50))
    describe = Column(String(255))           # 商品描述
    is_shelves = Column(Integer,default=0) # 是否上架，0：否  1：是
    price = Column(Integer)                    # 商品价格
    specifications = Column(Text)               # 商品规格
    create_time = Column(DateTime,default=datetime.datetime.now)
    cate_id = Column(Integer,ForeignKey('category.id'))
    cate = relationship('Category', backref=backref('goods'))


class GoodsImg(Base):
    __tablename__ = 'goodsimg'
    id = Column(Integer, primary_key=True)
    create_time = Column(DateTime, default=datetime.datetime.now)
    image = Column(String(255))
    img_order = Column(Integer,default=0)
    goods_id = Column(Integer, ForeignKey('goods.id'))
    goods = relationship('Goods', backref=backref('goodsimg'))


class Order(Base):
    __tablename__ = 'order'
    # id = Column(Integer,unique=True,autoincrement=True,nullable=False)
    id = Column(String(128),primary_key=True) # 主键为时间戳
    ststes = Column(Integer)  # 交易状态(0:待支付，1:已付款，2:以退款，3:交易关闭)
    order_amount = Column(Integer) # 订单金额
    payment_amount = Column(Integer) # 付款金额 （实际付款金额，使用优惠券后的）
    create_time = Column(DateTime,default=datetime.datetime.now)
    outer_traed_number = Column(String(128)) # 交易订单号 /第三方交易的订单号
    user_id = Column(Integer)


class OrderDetail(Base):
    __tablename__ = 'orderdetail'
    id = Column(Integer,primary_key=True)
    goodslist = Column(Text)  # 商品列表，json格式
    distribution_amoubt = Column(Integer) # 配送状态
    goods_address = Column(String(128))  # 收货地址
    order_id = Column(String(128),ForeignKey('order.id'))
    order = relationship('Order',backref=backref('orderdetail'))


class Coupons(Base):
    __tablename__ = 'coupons'
    id = Column(Integer,primary_key=True)
    types = Column(Integer,default=0)   # 优惠券类型，0：折扣
    code = Column(String(128))   # 优惠券码
    discount = Column(DECIMAL(3,2)) # 优惠券折扣数
    starting_time = Column(DateTime, default=datetime.datetime.now) # 优惠券起始时间
    erminationt_time= Column(DateTime)

class Comments(Base):
    __tablename__ = 'comments'
    id = Column(Integer,primary_key=True)
    content = Column(Text)
    user_id = Column(Integer)
    goods_id = Column(Integer)
    create_time = Column(DateTime, default=datetime.datetime.now)

# 秒杀商品表
class SecondsKill(Base):
    __tablename__ = 'secondskill'
    id = Column(Integer,primary_key=True)
    gname = Column(String(50))
    describe = Column(String(255))  # 商品描述
    is_shelves = Column(Integer, default=0)  # 是否上架，0：否  1：是
    price = Column(Integer)  # 商品价格
    specifications = Column(Text)  # 商品规格
    create_time = Column(DateTime, default=datetime.datetime.now)




if __name__ == '__main__':

    #建表
    Base.metadata.create_all()