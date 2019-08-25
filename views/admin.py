from .base import BaseHandler
from .models import User,Category,Goods,GoodsImg
from db import sess
import re,json,os
from sqlalchemy import func
from Decorator import rbac


class Login(BaseHandler):
    def get(self, *args, **kwargs):
        self.render('../templates/admin_page/login.html')
    def post(self):
        mes = {}
        username = self.get_argument('username')
        password = self.get_argument('password')
        if not all([username,password]):
            mes['message'] = '请输入账户密码'
            self.write('输入账户密码')
        elif re.match('\w{5,12}',username) is None:
            self.write('账号不符合规范')
        else:
            user = sess.query(User).filter(User.username == username).first()
            if user is not None:
                if user.password != password:
                    self.write('密码不正确')
                else:
                    self.set_cookie('userid',str(user.id))
                    self.redirect('/admin/index')
            else:
                self.write('没有该账号')


class Index(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        user_id = self.get_cookie('userid')
        if not user_id:
            self.redirect('/admin/login')
        else:
            print(self.request.uri, '0-0-0-0-0-0-0-0-0')
            data_box = {}
            user = sess.query(User).filter(User.id == user_id).first()
            data_box['user'] = user
            self.render('../templates/admin_page/index.html',**data_box)

class Welcome(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        self.render('../templates/admin_page/welcome.html')

class GetUser(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        data_box = {}
        user_all = sess.query(User).all()
        num = sess.query(func.count(User.id)).scalar()
        data_box['user_all'] = user_all
        data_box['num'] = num
        self.render('../templates/admin_page/user-list.html',**data_box)

class Modify(BaseHandler):
    @rbac
    def get(self):
        id = self.get_argument('id')
        if id:
            data_box = {}
            user_show = sess.query(User).filter(User.id == id).first()
            data_box['user_show'] = user_show
            self.render('../templates/admin_page/user-modify.html',**data_box)

    @rbac
    def post(self):
        id = self.get_argument('id')
        if id:
            data_box = {}
            user_show = sess.query(User).filter(User.id == id).first()
            nick = self.get_argument('nick')
            gender = self.get_argument('gender')
            phone = self.get_argument('phone')
            user_show.nick = nick
            user_show.gender = gender
            user_show.phone = phone
            self.redirect('/admin/user_list')

class DelUser(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        id = self.get_argument('id')
        if id:
            user = sess.query(User).filter(User.id == id).first()
            sess.delete(user)
            self.redirect('/admin/user_list')


class AddUser(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        self.render('../templates/admin_page/user-add.html')

    @rbac
    def post(self, *args, **kwargs):
        username = self.get_argument('username')
        password = self.get_argument('password')
        nick = self.get_argument('nick')
        gender = self.get_argument('gender')
        phone = self.get_argument('phone')
        email = self.get_argument('email')
        address = self.get_argument('address')
        if not all([username,password,nick,gender,phone]):
            self.write('信息不全')
        else:
            new_user = User(username=username,nick=nick,password=password,phone=phone,gender=gender)
            sess.add(new_user)
            self.redirect('/admin/user_list')



class Exit(BaseHandler):
    def get(self, *args, **kwargs):
        self.clear_cookie('user_id')
        self.redirect('/admin/login')


class ProductCategory(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        num = sess.query(func.count(Category.id)).scalar()
        category1 = sess.query(Category).filter(Category.parent_id == 0)
        data_box = {
            'num':num,
            'category_data':category1,
        }
        self.render('../templates/admin_page/product-category.html',**data_box)

class ProductCategory2(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        id = self.get_argument('id')
        cname = self.get_argument('cname')
        num = sess.query(func.count(Category.id)).scalar()
        category1 = sess.query(Category).filter(Category.parent_id == id)
        data_box = {
            'num':num,
            'cname':cname,
            'category_data':category1,
        }
        self.render('../templates/admin_page/product-category2.html',**data_box)

class ProductCategory3(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        id = self.get_argument('id')
        cname = self.get_argument('cname')
        num = sess.query(func.count(Category.id)).scalar()
        category1 = sess.query(Category).filter(Category.parent_id == id)
        data_box = {
            'num':num,
            'cname':cname,
            'category_data':category1,
        }
        self.render('../templates/admin_page/product-category3.html',**data_box)

class CateModify(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        id = self.get_argument('id')
        category = sess.query(Category).filter(Category.id == id).first()
        data_box = {
            'cname':category.cname,
        }
        self.render('../templates/admin_page/cate-modify.html',**data_box)

    @rbac
    def post(self, *args, **kwargs):
        id = self.get_argument('id')
        cname = self.get_argument('cname')
        category = sess.query(Category).filter(Category.id == id).first()
        if cname:
            category.cname = cname
            self.redirect('/admin/product_category')

class DelCate(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        id = self.get_argument('id')
        if id:
            category1 = sess.query(Category).filter(Category.id == id).first()
            pid1 = category1.id
            category2 = sess.query(Category).filter(Category.parent_id==pid1).all()
            if category2 != []:
                for i in category2:
                    pid2 = i.id
                    category3 = sess.query(Category).filter(Category.parent_id == pid2).all()
                    if category3 !=[]:
                        for j in category3:
                            pid3 = j.id
                            if pid3:
                                del_cate3 = sess.query(Category).filter(Category.id==pid3).first()
                                sess.delete(del_cate3)
                                del_cate2 = sess.query(Category).filter(Category.id == pid2).first()
                                sess.delete(del_cate2)
                                del_cate1 = sess.query(Category).filter(Category.id == pid1).first()
                                sess.delete(del_cate1)
                                self.redirect('/admin/product_category')
                    else:
                        del_cate2 = sess.query(Category).filter(Category.id == pid2).first()
                        sess.delete(del_cate2)
                        del_cate1 = sess.query(Category).filter(Category.id == pid1).first()
                        sess.delete(del_cate1)
                        self.redirect('/admin/product_category')
            else:
                del_cate1 = sess.query(Category).filter(Category.id == pid1).first()
                sess.delete(del_cate1)
                self.redirect('/admin/product_category')




class AddCategory(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        data_box = {}
        category = sess.query(Category).filter(Category.parent_id == 0)
        category2 = sess.query(Category).filter(Category.parent_id.in_([cate.id for cate in category]))
        data_box['category_data1'] = category
        data_box['category_data2'] = category2
        self.render('../templates/admin_page/product-category-add.html',**data_box)

    @rbac
    def post(self, *args, **kwargs):
        # cname1：一级分类    cname2：二级分类    cname3：三级分类
        # cate1：下拉框选择一级分类      cate2：下拉框选择二级分类
        cname1 = self.get_argument('cname1','')
        cname2 = self.get_argument('cname2','')
        cname3 = self.get_argument('cname3','')
        cate1 = self.get_argument('cate1','')
        cate2 = self.get_argument('cate2','')
        if cname1:
            category = Category(cname=cname1)
            sess.add(category)
            sess.commit()
            self.redirect('/admin/add_category')
        else:
            if cname2:
                category = Category(cname=cname2,parent_id=cate1)
                sess.add(category)
                sess.commit()
                self.redirect('/admin/add_category')
            else:
                if cname3:
                    category = Category(cname=cname3,parent_id=cate2)
                    sess.add(category)
                    sess.commit()
                    self.redirect('/admin/add_category')

# 商品展示
class GoodsList(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        goodsList = sess.query(Goods).all()
        data_box = {
            'goodsList':goodsList,
        }
        self.render('../templates/admin_page/goods-list.html',**data_box)


# 商品添加
class GoodsAdd(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        cateList = sess.query(Category).all()
        data_box = {
            'cateList':cateList,
        }
        self.render('../templates/admin_page/goods-add.html',**data_box)

    @rbac
    def post(self, *args, **kwargs):
        gname = self.get_argument('gname','')
        describe = self.get_argument('describe','')
        price = self.get_argument('price','')
        specifications = self.get_argument('specifications','')
        is_shelves = self.get_argument('is_shelves','')
        cate = self.get_argument('cate','')
        speSring = specifications.split(',')
        speList = []
        for i in speSring:
            data = i.split(':')
            speDict = {data[0]:data[1]}
            speList.append(speDict)
        speContent = json.dumps(speList,ensure_ascii=False)
        goods = Goods(gname=gname,describe=describe,price=price,specifications=speContent,is_shelves=is_shelves,cate_id=cate)
        sess.add(goods)
        sess.commit()
        self.redirect('/admin/goods_list')

# 商品修改
class UpdateGoods(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        id = self.get_argument('id')
        cateList = sess.query(Category).all()
        goods = sess.query(Goods).filter(Goods.id == id).first()
        data_box = {
            'cateList': cateList,
            'goods':goods
        }
        self.render('../templates/admin_page/goods-update.html',**data_box)

    @rbac
    def post(self, *args, **kwargs):
        id = self.get_argument('id')
        gname = self.get_argument('gname')
        describe = self.get_argument('describe')
        specifications = self.get_argument('specifications')
        price = self.get_argument('price')
        cate = self.get_argument('cate')
        if id:
            goods = sess.query(Goods).filter(Goods.id == id).first()
            goods.gname = gname
            goods.describe = describe
            goods.specifications = specifications
            goods.price = price
            goods.cate_id = cate
            self.redirect('/admin/goods_list')

# 商品删除
class DelGoods(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        id = self.get_argument('id')
        if id:
            goods = sess.query(Goods).filter(Goods.id == id).first()
            sess.delete(goods)
            sess.commit()
            self.redirect('/admin/goods_list')

# 修改商品上架/下架
class GoodsShelves(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        id = self.get_argument('id')
        goods = sess.query(Goods).filter(Goods.id == id).first()
        if goods.is_shelves == 1:
            goods = sess.query(Goods).filter(Goods.id == id).first()
            goods.is_shelves = 0
            self.redirect('/admin/goods_list')
        else:
            goods = sess.query(Goods).filter(Goods.id == id).first()
            goods.is_shelves = 1
            self.redirect('/admin/goods_list')



# 图片首页展示
class Picture(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        goodsimg = sess.query(GoodsImg).all()
        data_box = {
            'goodsimg':goodsimg,
        }

        self.render('../templates/admin_page/picture-list.html',**data_box)


# 删除图片
class DelPicture(BaseHandler):
    @rbac
    def get(self, *args, **kwargs):
        id = self.get_argument('id')
        if id:
            img = sess.query(GoodsImg).filter(GoodsImg.id == id).first()
            sess.delete(img)
            sess.commit()
            self.redirect('/admin/picture')

#上传文件
class UploadHandler(BaseHandler):
    @rbac
    async def get(self):
        goodsList = sess.query(Goods).all()
        data_box = {'goodsList':goodsList}
        self.render('../templates/admin_page/upload.html',**data_box)

    @rbac
    async def post(self):

        #上传路径
        upload_path = os.path.dirname(os.path.dirname(__file__))+"/static/upload/"

        #接收文件，以对象的形式
        img = self.request.files.get('file', None)
        name = int(self.get_argument('name','未收到'))
        num = int(self.get_argument('num','未收到'))
        for meta in img:
            filename = meta['filename']
            file_path = upload_path + filename
            with open(file_path, 'wb') as up:
                up.write(meta['body'])

            goodsimg = GoodsImg(image=filename,img_order=num,goods_id=name)
            sess.add(goodsimg)
            sess.commit()

        self.write(json.dumps({'status':'ok'},ensure_ascii=False))


# 反向查询  通过backref=backref('goods')查询
# b = sess.query(Category).filter(Category.id == 27).first()
#         a = b.goods[0]
#         print(a)

# 正向查询 cate = relationship('Category', backref=backref('goods')) 通过字段名cate查询
# 反向查询  通过backref=backref('goods')查询
# b = sess.query(Goods).filter(Goods.id == 7).first()
#         a = b.cate
#         print(a)



# data = [{'id':1,'name':'名称1','pid':0},{'id':2,'name':'名称2','pid':1},{'id':3,'name':'名称3','pid':2}]
# def xTree(datas):
#     lists=[]
#     tree={}
#     parent_id=''
#     for i in datas:
#         item=i
#         tree[item['id']]=item
#     root=None
#     for i in datas:
#         obj=i
#         if not obj['pid']:
#             root=tree[obj['id']]
#             lists.append(root)
#         else:
#             parent_id=obj['pid']
#             if 'children' not in tree[parent_id]:
#                 tree[parent_id]['children']=[]
#             tree[parent_id]['children'].append(tree[obj['id']])
#     return lists
#
# print(xTree(data))





