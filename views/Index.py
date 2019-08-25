from .base import BaseHandler


class IndexHandler(BaseHandler):
    def get(self, *args, **kwargs):
        # self.write("Hello, world123")
        # self.finish({'name':'你好'})
        self.write('Hello World')


class Login(BaseHandler):
    async def get(self):
        data_box = {}
        data_box['index_word'] = 'Hello World'
        self.render('../templates/admin_page/login.html', **data_box)













