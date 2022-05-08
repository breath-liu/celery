import datetime
import time

import celery
from celery.exceptions import Ignore
from celery.utils.log import get_task_logger

from .BaseRetryTask import BaseTaskWithRetry
from .Custom import MyTask
from .celery import app
from celery.worker.control import control_command

logger = get_task_logger(__name__)


@app.task(name='a=b=c')
def add(x, y):
    logger.info(f'add {x},{y}')
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)


@app.task(bind=True)
def dump_context(self, x, y, **kwargs):
    print(self.request.id)
    print('Executing task id {0.id}, args: {0.args!r} kwargs: {0.kwargs!r}'.format(
        self.request))


@app.task(bind=True, default_retry_delay=4)
def retry_test(self):
    print(self.request.__dict__)
    sec = datetime.datetime.now().second
    try:
        if sec % 2 == 0:
            raise Exception("ex")
        else:
            print(f'========={sec}')
    except Exception as exc:
        self.retry(exc=exc)


@app.task(base=BaseTaskWithRetry, rate_limit='1/m')
def retry_inherit():
    sec = datetime.datetime.now().second
    if sec % 4 != 0:
        raise Exception("ex")
    else:
        print(f'========={sec}')


@app.task()
def ignore_test():
    print('igore')
    raise Ignore()


@app.task(bind=True, base=BaseTaskWithRetry, autoretry_for=(Exception,))
def init_task(self):
    print(self.request.__dict__)
    print(1111)
    raise Exception('ex')


@app.task
def error_handler(request, exc, traceback):
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(
        request.id, exc, traceback))


@app.task(bind=True, base=BaseTaskWithRetry)
def hello(self, a, b):
    time.sleep(1)
    self.update_state(state="PROGRESS", meta={'progress': 50})
    time.sleep(6)
    self.update_state(state="PROGRESS", meta={'progress': 90})
    time.sleep(1)
    return 'hello world: %i' % (a + b)



