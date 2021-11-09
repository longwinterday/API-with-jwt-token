"""
Представления CBV эндпоинтов
"""
import datetime
import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from .serializers import UserSerializer
from .models import User, Message


class Registration(APIView):

    @classmethod
    def post(cls, request) -> Response:
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LogInView(APIView):

    @classmethod
    def post(cls, request) -> Response:
        name = request.data.get('name')
        password = request.data.get('password')
        user = User.objects.filter(name=name).first()

        # невозможность получить токен незарегистрированному пользователю
        if user is None:
            raise AuthenticationFailed('Пользователь с таким именем не обнаружен')

        # невозможность получить токен если неверный пароль
        if not user.check_password(password):
            raise AuthenticationFailed('Неверный пароль')

        payload = {
            'name': user.name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow(),
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)

        response.data = {'token': token}

        return response


class MessageView(APIView):

    @classmethod
    def post(cls, request) -> Response:
        token = request.headers.get('jwt')
        name = request.data.get('name')
        message = request.data.get('message')

        # валидация наличия значения у message
        if message is None:
            raise ValidationError('Обязательно наличие сообщения')

        # проверка наличия токена в приоритете в заголовках запроса далее в куки
        if token is None:
            token = request.COOKIES.get('jwt')
            if token is None:
                raise AuthenticationFailed('Вы не аутентифицированы или в заголовках отсутствует токен')

        # проверка токена на срок действия
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Время сессии истекло, авторизуйтесь заново или получите новый токен')

        user = User.objects.filter(name=payload.get('name')).first()

        # валидация запроса по токену
        if name != user.name:
            raise AuthenticationFailed('Нельзя отправлять сообщения от другого имени пользователя.')

        response = Response()

        # обработка сообщения содержащего команду history N
        try:
            history, count = message.split(' ')
            count = int(count)
            if history == 'history' and count > 0:
                response.data = dict()
                for i_message in Message.objects.filter(user=user).all()[:count]:
                    response.data[i_message.id] = i_message.message_text
        except ValueError:
            Message.objects.create(user=user, message_text=message)
            response.data = {'message': 'Сообщение успешно загружено'}

        return response


class LogOutView(APIView):

    @classmethod
    def post(cls, request) -> Response:
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Успешный выход из системы'
        }
        return response
