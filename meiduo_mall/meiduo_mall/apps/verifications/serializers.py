from django_redis import get_redis_connection
from redis import RedisError
from rest_framework import serializers

import logging

logger = logging.getLogger('meiduo')


class ImageCodeCheckSerializer(serializers.Serializer):
    """校验图片验证码的序列化器"""
    image_code_id = serializers.UUIDField()
    image_code_text = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        image_code_id = attrs['image_code_id']
        image_code_text = attrs['image_code_text']
        # 获取存储在redis中的图片验证码，以便进行比对
        redis_conn = get_redis_connection('Image_code')
        redis_image_code = redis_conn.get('img_%s' % image_code_id)
        # 为了减少验证码不断刷新，造成存储过大，每次请求完，删除该验证码
        if not redis_image_code:
            raise serializers.ValidationError('图片验证码无效')
        try:
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as e:
            logger.error(e)
        # 验证码不区分大小写，故全转小写再进行比较
        if image_code_text.lower() != redis_image_code.decode().lower():
            raise serializers.ValidationError('图片验证码错误')
        moblie = self.context['view'].kwargs['moblie']

        send_flag = redis_conn.get('send_flag_%s' % moblie)
        if send_flag:
            raise serializers.ValidationError('请勿频繁发短信，一分钟只可发一次')
        return attrs
