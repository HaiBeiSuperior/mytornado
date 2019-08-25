import jwt
from settings import jwt_code
from views.models import User,Nodes,Roles,Role2Node
from db import sess
from settings import admin_url

# jwt验证装饰器
def decorator(views):
    def jwt_login(self,*args,**kwargs):
        mes = {}
        u_name = self.get_argument('u_name')
        token = self.get_argument('token')
        if all([u_name,token]) and u_name == jwt.decode(token,jwt_code,algorithms=['HS256'])['u_name']:
            mes['code'] = 200
            mes['message'] = '成功'
            return views(self,*args,**kwargs)
        else:
            mes['code'] = 10001
            mes['message'] = '数据类型错误'
    return jwt_login


# rbac验证权限装饰器

def rbac(views):
    def charm_permissions(self,*args,**kwargs):
        # 获得当前url
        current = self.request.uri
        user_id = self.get_cookie('userid')
        my_access = sess.query(Nodes.node_url,User.role_id).join(Roles,User.role_id == Roles.id).join(Role2Node,Roles.id == Role2Node.role_id).join(Nodes,Role2Node.node_id == Nodes.id).filter(User.id == user_id).all()
        urlList = []
        for val in my_access:
            urlList.append(val[0])
        if current in urlList:
            return views(self,*args,**kwargs)
        else:
            pass
    return charm_permissions












