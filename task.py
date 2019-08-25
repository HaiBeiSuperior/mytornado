import time
from celery import Celery
from func_tool import sendmail

C_FORCE_ROOT=True

celery = Celery("tasks", broker="amqp://guest:guest@localhost:5672")
celery.conf.CELERY_RESULT_BACKEND = "amqp"


@celery.task
def sleep(seconds):
    time.sleep(float(seconds))
    return seconds

@celery.task
def mail(email,nick):
    sendmail(email,nick)
    return '发送邮件成功'

if __name__ == "__main__":
    celery.start()