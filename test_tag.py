from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import User, Tag, AnswerRecord, Question,AdminUser
from .config.config import main
from unittest.mock import patch
from unittest.mock import Mock

class TagTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = '1926415776@qq.com'
        self.session = self.client.session
        self.tag_url=reverse('getAllTags')

    def test_get_all_tags_success(self):
        Tag.objects.create(tag='Math', create_time=timezone.now())
        Tag.objects.create(tag='Science', create_time=timezone.now())
        response = self.client.get(self.tag_url)
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        self.assertTrue(json_response['status'])
        self.assertEqual(json_response['code'], 200)
        self.assertEqual(json_response['msg'], '获取题目分类成功')
        self.assertEqual(len(json_response['data']), 2)
        self.assertEqual(json_response['data'][0]['tag'], 'Math')
        self.assertEqual(json_response['data'][1]['tag'], 'Science')

    def test_get_all_tags_failure(self):
        Tag.objects.all().delete()
        response = self.client.get(self.tag_url)
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        self.assertFalse(json_response['status'])
        self.assertEqual(json_response['code'], 500)
        self.assertEqual(json_response['msg'], '没有查询到数据')

