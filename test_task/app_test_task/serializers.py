"""
Сериалайзер модели пользователя с хэшированием пароля
"""
from rest_framework.serializers import ModelSerializer
from .models import User, Message


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'name', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(password)
            user.save()
            return user


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'user', 'message_text']
