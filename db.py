from sqlalchemy import create_engine # 创建引擎对象的模块
from sqlalchemy.orm import sessionmaker # 创建和数据库连接会话
# from sqlalchemy import Column,String,Integer # 内置的创建类的方法属性
from sqlalchemy.ext.declarative import declarative_base # 基础类模块
from sqlalchemy.ext.declarative import DeclarativeMeta #解码模块
import json
import datetime

# sqlalchemy默认底层使用 mysqldb 完成和数据库的连接
# 但是 mysqldb 不支持最新版本的 python 和 mysql 数据库的连接，一般用Pymysql进行替代。
import pymysql
pymysql.install_as_MySQLdb()

# 创建数据库引擎，数据库的类名、账号、密码、登录方式、连接的数据库、数据库编码、是否显示回写
engine =create_engine('mysql://root:@localhost:3306/mytornado',
                    encoding='utf-8',echo=True)

# 创建会话对象
Session=sessionmaker(bind=engine)
sess=Session()
# 2.如果创建会话的时候还没有创建引擎对象
# Session = sessionmaker()# 创建一个会话类型
# Session.configur(bind=engine)# 将一个连接引擎注册给这个会话
#dbsession = Session() # 得到具体的包含连接引擎的会话

# 创建基础类
Base=declarative_base(bind=engine)


def sqlalchemy_json(self):
    obj_dict = self.__dict__
    return dict((key, obj_dict[key]) for key in obj_dict if not key.startswith("_"))


Base.__json__ = sqlalchemy_json


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:  # 添加了对datetime的处理
                    if isinstance(data, datetime.datetime):
                        fields[field] = data.isoformat()
                    elif isinstance(data, datetime.date):
                        fields[field] = data.isoformat()
                    elif isinstance(data, datetime.timedelta):
                        fields[field] = (datetime.datetime.min + data).time().isoformat()
                    else:
                        fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)

