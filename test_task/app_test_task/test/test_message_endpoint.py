"""
Тест эндпоина message
"""
import datetime
import jwt
from time import sleep
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse_lazy
from rest_framework.exceptions import AuthenticationFailed
from ..models import Message, User


class MessageEndpointTest(APITestCase):

    def setUp(self) -> None:
        self.name = 'user1'
        self.password = 'user1'
        self.message = 'Test'
        self.history_message = 'history 10'
        self.data_messages = [f'test{i}' for i in range(1, 20)]
        self.client.post(reverse_lazy('registration'), {'name': self.name, 'password': self.password})
        self.user = User.objects.filter(name=self.name).first()

    # получаем корректный код ответа от сервера через куки
    def test_can_get_correct_response_via_cookie(self):
        self.client.post(reverse_lazy('login'), {'name': self.name, 'password': self.password})
        response = self.client.post(reverse_lazy('message'), {'name': self.name, 'message': self.message})
        self.assertEqual(response.status_code, 200)

    # получаем корректный код ответа от сервера передав в заголовках токен
    def test_can_get_correct_response_via_token(self):
        payload = {
            'name': self.name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow(),
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        c = APIClient(HTTP_JWT=token)
        response = c.post(reverse_lazy('message'), {'name': self.name, 'message': self.message})
        self.assertEqual(response.status_code, 200)

    # проверяем невозможность создать сообщение по просроченному токену
    def test_expired_token(self):
        payload = {
            'name': self.name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1),
            'iat': datetime.datetime.utcnow(),
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        sleep(2)
        c = APIClient(HTTP_JWT=token)
        response = c.post(reverse_lazy('message'), {'name': self.name, 'message': self.message})
        self.assertRaisesMessage(response, jwt.ExpiredSignatureError)

    # проверяем невозможность создать сообщение по токену не совпадающему с именем пользователя
    def test_wrong_token(self):
        payload = {
            'name': self.name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow(),
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        c = APIClient(HTTP_JWT=token)
        response = c.post(reverse_lazy('message'), {'name': 'user2', 'message': self.message})
        self.assertRaisesMessage(response, AuthenticationFailed)

    # проверяем возможность создания сообщения через токен в заголовках без куки
    def test_can_create_messages_via_token(self):
        payload = {
            'name': self.name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow(),
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        c = APIClient(HTTP_JWT=token)
        c.post(reverse_lazy('message'), {'name': self.name, 'message': self.message})
        message_text = Message.objects.first().message_text
        self.assertEqual(message_text, self.message)

    # проверяем возможность получения 10 последних сообщений из БД по особому message через куки
    def test_can_show_history_via_cookie(self):
        for i_message in self.data_messages:
            Message.objects.create(user=self.user, message_text=i_message)
        self.client.post(reverse_lazy('login'), {'name': self.name, 'password': self.password})
        response = self.client.post(reverse_lazy('message'), {'name': self.name, 'message': self.history_message})
        self.assertEqual([i for i in response.data.values()],
                         sorted(self.data_messages, reverse=True, key=lambda x: self.data_messages.index(x))[:10])
