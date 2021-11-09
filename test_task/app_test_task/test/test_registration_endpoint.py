"""
Тест эндпоинта registration
"""
from rest_framework.test import APITestCase
from django.urls import reverse_lazy
from ..models import User


class RegistrationEndpointTest(APITestCase):

    def setUp(self) -> None:
        self.name = 'user1'
        self.password = 'user1'

    # получаем корректный код ответа от сервера
    def test_can_get_correct_response(self):
        response = self.client.post(reverse_lazy('registration'), {'name': self.name, 'password': self.password})
        self.assertEqual(response.status_code, 200)

    # получаем некорректный код ответа от сервера не передав пароль
    def test_can_get_incorrect_response(self):
        response = self.client.post(reverse_lazy('registration'), {'name': self.name})
        self.assertEqual(response.status_code, 400)

    # проверяем возможность создания пользователя
    def test_can_create_user(self):
        self.client.post(reverse_lazy('registration'), {'name': self.name, 'password': self.password})
        user = User.objects.get(name=self.name)
        self.assertEqual(user.name, self.name)

    # проверяем невозможность создания дубликата пользователя
    def test_can_not_create_duplicate_user(self):
        self.client.post(reverse_lazy('registration'), {'name': self.name, 'password': self.password})
        response = self.client.post(reverse_lazy('registration'), {'name': self.name, 'password': self.password})
        users = User.objects.filter(name=self.name).all()
        self.assertEqual(len(users), 1)
        self.assertEqual(response.status_code, 400)
