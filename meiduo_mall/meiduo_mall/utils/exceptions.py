import logging

from django.db import DatabaseError
from redis.exceptions import RedisError
from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger('meiduo')


# 封装异常处理，以便输出日志错误信息（因为django原本不会识别数据库错误信息）
def exception_handle(exc, context):
    """
        自定义异常处理
        :param exc: 异常
        :param context: 抛出异常的上下文
        :return: Response响应对象
    """
    response = drf_exception_handler(exc, context)
    if response is None:
        view = context['view']
        if isinstance(exc, DatabaseError) or isinstance(exc, RedisError):
            logger.error('[%s] %s' % (view, exc))
            response = Response({'message': '服务器内部出错'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
    return response
