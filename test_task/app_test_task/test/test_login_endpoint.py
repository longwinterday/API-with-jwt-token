"""
Тест эндпоинта login
"""
import jwt
from rest_framework.test import APITestCase
from django.urls import reverse_lazy
from rest_framework.exceptions import AuthenticationFailed


class LogInEndpointTest(APITestCase):

    def setUp(self) -> None:
        self.name = 'user1'
        self.password = 'user1'
        self.client.post(reverse_lazy('registration'), {'name': self.name, 'password': self.password})

    # получаем корректный код ответа от сервера
    def test_can_get_correct_response(self):
        response = self.client.post(reverse_lazy('login'), {'name': self.name, 'password': self.password})
        self.assertEqual(response.status_code, 200)

    # получаем не корректный код ответа от сервера из-за отсутствия пароля
    def test_can_get_incorrect_response(self):
        response = self.client.post(reverse_lazy('login'), {'name': self.name})
        self.assertEqual(response.status_code, 403)

    # проверяем невозможность получения токена незарегистрированным пользователем
    def test_user_not_found(self):
        response = self.client.post(reverse_lazy('login'), {'name': 'user2', 'password': self.password})
        contains = 'Пользователь с таким именем не обнаружен' in str(response.data.get('detail'))
        self.assertRaisesMessage(response, AuthenticationFailed)
        self.assertTrue(contains)

    # проверяем невозможность получения токена если пользователь предоставил неверный пароль
    def test_incorrect_password(self):
        response = self.client.post(reverse_lazy('login'), {'name': self.name, 'password': 'bad_password'})
        contains = 'Неверный пароль' in str(response.data.get('detail'))
        self.assertRaisesMessage(response, AuthenticationFailed)
        self.assertTrue(contains)

    # проверяем корректность получения токена
    def test_can_get_token(self):
        response = self.client.post(reverse_lazy('login'), {'name': self.name, 'password': self.password})
        token = response.data.get('token')
        user_name = None
        if token:
            user_name = jwt.decode(token, 'secret', algorithms=['HS256']).get('name')
        self.assertEqual(user_name, self.name)

    # проверяем наличие токена в куки
    def test_can_get_cookie(self):
        response = self.client.post(reverse_lazy('login'), {'name': self.name, 'password': self.password})
        token = response.data.get('token')
        contains = str(token) in str(response.cookies)
        self.assertTrue(contains)
