# -*- coding: utf-8 -*-

"""提供logger给其他文件调用"""

import os
import logging
import logging.config
import functools

project_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
logger_conf_path = project_path + '/conf/logging.conf'
logging.config.fileConfig(logger_conf_path)
logger = logging.getLogger('yingyonghui')

# logger.info('logger start')

def Timer(func):
    """
    提供一个装饰器，用以统计函数运行时间

    Args:
        func: 被包装的函数
    Returns:
        _wrapper: function object, callable
    """
    import time

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        start = int(time.time())
        result = func(*args, **kwargs)
        end = int(time.time())
        logger.info('%s() Done. Elapsed %ss.' % (func.__name__, end - start))
        return result

    return _wrapper


if __name__ == '__main__':
    @Timer
    def foo(arg1, kwarg1='default'):
        logger.debug('in foo(%s, kwarg1=%s)' % (arg1, kwarg1))
        return 'haha'

    logger.debug(foo('test_Timer'))
