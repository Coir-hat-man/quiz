from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import User, Tag, AnswerRecord, Question,AdminUser
from .config.config import main
from unittest.mock import patch
from unittest.mock import Mock

class LogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.email_url=reverse('getemailcode')
        self.email = '1926415776@qq.com'
        self.session = self.client.session
        self.session['info'] = True  # 模拟已登录状态
        self.session.save()

    def test_user_log(self):
        response = self.client.get(self.login_url)
        self.assertRedirects(response, '/shuati_app/')  # 已登录时应该重定向到控制台
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/shuati_app/login/?message=退出登录成功！')

