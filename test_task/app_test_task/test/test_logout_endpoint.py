"""
Тесты эндпоинта logout
"""
from rest_framework.test import APITestCase
from django.urls import reverse_lazy


class LogOutEndpointTest(APITestCase):

    def setUp(self) -> None:
        self.name = 'user1'
        self.password = 'user1'
        self.client.post(reverse_lazy('registration'), {'name': self.name, 'password': self.password})

    # получаем корректный код ответа от сервера
    def test_can_get_correct_response(self):
        response = self.client.post(reverse_lazy('logout'))
        self.assertEqual(response.status_code, 200)

    # проверяем наличие куки с jwt после logout
    def test_clean_cookies(self):
        response1 = self.client.post(reverse_lazy('login'), {'name': self.name, 'password': self.password})
        token = response1.data.get('token')
        contains = str(token) in str(response1.cookies)
        response2 = self.client.post(reverse_lazy('logout'))
        contains2 = str(token) in str(response2.cookies)
        self.assertTrue(contains)
        self.assertFalse(contains2)
