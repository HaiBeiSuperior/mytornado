import tornado.web
from views import Index
from views import admin
from views import users
from views import mall
import config


#路由

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/celery", users.CeleryHandler),
            (r"/", Index.IndexHandler),
            (r"/admin/login", admin.Login),
            (r"/admin/index", admin.Index),
            (r"/admin/welcome", admin.Welcome),
            (r"/admin/user_list", admin.GetUser),   # 用户管理
            (r"/admin/user_modify", admin.Modify),  # 用户修改
            (r"/admin/delete_user", admin.DelUser), # 用户删除
            (r"/admin/add_user", admin.AddUser),    # 用户添加
            (r"/admin/exit", admin.Exit),
            (r"/admin/product_category", admin.ProductCategory),
            (r"/admin/product_category2", admin.ProductCategory2),
            (r"/admin/product_category3", admin.ProductCategory3),
            (r"/admin/cate_modify", admin.CateModify),
            (r"/admin/del_cate", admin.DelCate),
            (r"/admin/add_category", admin.AddCategory),
            (r"/admin/goods_list", admin.GoodsList),
            (r"/admin/goods_add", admin.GoodsAdd),
            (r"/admin/update_goods", admin.UpdateGoods),
            (r"/admin/delete_goods", admin.DelGoods),
            (r"/admin/goods_shelves", admin.GoodsShelves),
            (r"/admin/picture", admin.Picture),
            (r"/admin/del_picture", admin.DelPicture),
            (r"/upload", admin.UploadHandler),
            (r"/users/login", users.UserLogin),
            (r"/users/register", users.UserRegister),
            (r"/users/getcode", users.GetCode),
            (r"/users/send", users.Send),
            (r"/user/login/qq_login", users.QQ_login),
            (r"/get_authorization_code", users.Get_authorization_code),
            # (r"/users/exitcode", users.Exitcode),
            (r"/users/sinafirsthandler", users.SinaFirstHandler),
            (r"/mall/index", mall.Index),
            (r"/mall/get_goods_list", mall.GetGoodss),
            (r"/mall/get_goods", mall.GetGoods),
            (r"/mall/storage_redis", mall.StorageRedis),
            (r"/mall/total_user", mall.TreeHandler),
            (r"/mall/search_content", mall.SearchContent),
            (r"/mall/coupons", mall.GetCoupons),
            (r"/mall/get_order", mall.GetOrder),
            (r"/mall/refund", mall.Refund),
            (r"/mall/published_comment", mall.PubComments),
            (r"/mall/get_comment", mall.GrtComments),
            (r"/page", mall.PayPageHandler),
            (r"/alipayreturn", mall.PayRetrunHandler),
            (r"/md_admin/weibo", users.SinaBackHandler),
        ]
        super(Application,self).__init__(handlers,**config.setting)