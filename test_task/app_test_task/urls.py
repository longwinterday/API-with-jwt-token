"""
Urls эндпоинтов
"""
from django.urls import path
from .views import Registration, LogInView, MessageView, LogOutView

urlpatterns = [
    path('registration', Registration.as_view(), name='registration'),
    path('login', LogInView.as_view(), name='login'),
    path('message', MessageView.as_view(), name='message'),
    path('logout', LogOutView.as_view(), name='logout'),
]
