from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import User, Tag, AnswerRecord, Question,AdminUser
from .config.config import main
from unittest.mock import patch
from unittest.mock import Mock

class GetRandomQuestionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('getRandomQuestion')
        # 创建用户
        self.user = User.objects.create(username='testuser', email='test@example.com')
        # 设置会话信息
        session = self.client.session
        session['username'] = self.user.username
        session['email'] = self.user.email
        session.save()
        # 创建标签和问题
        self.tag = Tag.objects.create(tag='Math', create_time=timezone.now())
        # 创建一个题目对象
        self.question = Question.objects.create(
            question_id='Q001',
            question_content='What is 2+2?',
            options={
                "A": "1",
                "B": "2",
                "C": "3",
                "D": "4"
            },
            correct_answer='D',
            tag=self.tag,
            answer_detail='The correct answer is 4. A real difficult question.'
        )

    def test_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertFalse(json_response['status'])
        self.assertEqual(json_response['msg'], '没有登录，无权访问')

    def test_user_identity_check_failed(self):
        response = self.client.get(self.url, {'username': 'wronguser', 'email': 'wrongemail'})
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertFalse(json_response['status'])
        self.assertEqual(json_response['msg'], '用户身份校验未通过，获取题目信息失败')

    def test_no_questions_for_tag(self):
        response = self.client.get(self.url,
                                   {'username': self.user.username, 'email': self.user.email, 'tag_nid': '2',
                                    'tag_tag': 'Science'})
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertFalse(json_response['status'])
        self.assertEqual(json_response['msg'], '此标签暂时没有题目，等待管理员添加中...')

    @patch('shuati_app.services.record_service.RecordService.select_record_by_question')
    def test_get_questions_success(self, mock_select_record_by_question):
        mock_select_record_by_question.return_value = AnswerRecord.objects.filter(question=self.question)
        response = self.client.get(self.url, {'username': self.user.username, 'email': self.user.email,
                                              'tag_nid': self.tag.nid, 'tag_tag': self.tag.tag})
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertTrue(json_response['status'])
        self.assertEqual(json_response['msg'], '获取题目成功')


    @patch('shuati_app.services.question_service.QuestionService.select_question_exclude')
    def test_select_question_exclude(self, mock_select_question_exclude):
        mock_select_question_exclude.return_value =None
        response = self.client.get(self.url, {'username': self.user.username, 'email': self.user.email,
                                              'tag_nid': self.tag.nid, 'tag_tag': self.tag.tag})
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertFalse(json_response['status'])
        self.assertEqual(json_response['msg'], '此标签的题目已经全部被您刷完啦！去其他的分类看看吧')