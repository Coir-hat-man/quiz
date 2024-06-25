from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import User, Tag, AnswerRecord, Question,AdminUser
from .config.config import main
from unittest.mock import patch
from unittest.mock import Mock

class AdminLoginTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('adminlogin')
        self.admin_username = 'admin'
        self.admin_password = 'admin123'
        self.admin_user = AdminUser.objects.create(username=self.admin_username, password=self.admin_password)
        self.session = self.client.session
        self.session['info'] = True  # 模拟已登录状态
        self.session.save()


    def test_get_login_page(self):
        # 发起 GET 请求
        response = self.client.get(self.login_url)

        # 断言应该返回登录页面
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'adminsite/adminlogin.html')

    @patch('shuati_app.services.admin_service.Admin_admin_Service.select_admin')
    def test_admin_login_success(self, mock_select_admin):
        # 模拟 select_admin 返回存在的用户
        mock_select_admin.return_value.exists.return_value = True

        # 构造 POST 数据
        login_data = {
            'username': self.admin_username,
            'password': self.admin_password,
        }

        # 发起 POST 请求
        response = self.client.post(self.login_url, login_data)

        # 断言应该重定向到管理员控制台页面
        self.assertRedirects(response, '/shuati_app/adminconsole/')

        # 检查 session 是否正确设置
        self.assertTrue(self.client.session.get("admin_username"))
        self.assertTrue(self.client.session.get("is_admin"))
        self.assertTrue(self.client.session.get("is_logined"))


    @patch('shuati_app.services.admin_service.Admin_admin_Service.select_admin')
    def test_admin_login_failure(self, mock_select_admin):
        # 模拟 select_admin 返回不存在的用户
        mock_select_admin.return_value.exists.return_value = False

        # 构造 POST 数据，使用错误的用户名和密码
        login_data = {
            'username': 'wrong_username',
            'password': 'wrong_password',
        }

        # 发起 POST 请求
        response = self.client.post(self.login_url, login_data)

        # 断言应该返回登录页面，并且包含错误消息
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'adminsite/adminlogin.html')
        self.assertContains(response, "用户名或者密码不正确")
