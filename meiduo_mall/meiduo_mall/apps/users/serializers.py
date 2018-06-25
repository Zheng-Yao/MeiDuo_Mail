import re

from django_redis import get_redis_connection
from rest_framework import serializers
from .models import User
from rest_framework_jwt.settings import api_settings


class CreateUserSerializer(serializers.ModelSerializer):
    """创建用户序列化器"""
    password2 = serializers.CharField(label='确认密码', required=True, allow_null=False, write_only=True, allow_blank=False)
    sms_code = serializers.CharField(label='短信验证码', required=True, allow_null=False, write_only=True, allow_blank=False)
    allow = serializers.CharField(label='同意协议', required=True, allow_null=False, allow_blank=False, write_only=True)
    token = serializers.CharField(label='登录状态token', read_only=True)  # 增加token字段

    # 数据校验
    def validate_moblie(self, value):
        """验证手机号码"""
        if not re.match(r'^1[3-9]\d{9}', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        """验证是否勾选"""
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, attrs):
        # 验证两次输入的密码是否一致
        print(attrs)
        pwd1 = attrs['password']
        pwd2 = attrs['password2']
        if pwd1 != pwd2:
            raise serializers.ValidationError('两次输入密码不一致')
        # 判断短信验证码是否输入正确
        moblie = attrs['moblie']
        redis_conn = get_redis_connection('Image_code')
        real_sms_code = redis_conn.get('sms_%s' % moblie)
        sms_code = attrs['sms_code']
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码不正确')
        return attrs

    def create(self, validated_data):
        """创建用户，增添至数据库中"""
        # 清掉不必要的字段
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        # 创建字段
        user = super().create(validated_data)
        # 密码加密

        user.set_password(validated_data['password'])
        user.save()

        # 补充生成记录登陆状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        user.token = jwt_encode_handler(payload)

        return user

    # 关联模型类User
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'moblie', 'allow', 'token')
        # 序列化器字段自定义错误信息校验
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }
