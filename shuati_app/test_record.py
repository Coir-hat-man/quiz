from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import User, Tag, AnswerRecord, Question,AdminUser
from .config.config import main
from unittest.mock import patch
from unittest.mock import Mock

class GetRecordTest(TestCase):

    def setUp(self):
        self.user_email = 'testuser@examplee.com'
        self.user_username = 'testuser1'
        self.user=User.objects.create(username=self.user_username,email=self.user_email)
        self.session = self.client.session
        self.session['username'] = self.user_username
        self.session['email'] = self.user_email
        self.session.save()
        self.url = reverse('getRecord')
        self.tag=Tag.objects.create(tag='Math', create_time=timezone.now())
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
        self.keyword='What'

    @patch('shuati_app.services.user_service.UserService.select_user')
    @patch('shuati_app.services.record_service.RecordService.select_record_by_keyword')
    def test_get_record_success(self, mock_select_record_by_keyword, mock_select_user):

        mock_user_instance = self.user
        mock_select_user.return_value.first.return_value = mock_user_instance

        # Mock select_record_by_keyword to return a list of mock records
        mock_record_1 = AnswerRecord.objects.create(
            record_id="1",
            user=self.user,
            question=self.question,
            answer="A",
            is_correct=True,
            isInErrorBook=False
        )

        mock_select_record_by_keyword.return_value = AnswerRecord.objects.filter(
                is_delete=False, user=self.user,
                question__question_content__contains=self.keyword
            )


        # Simulate GET request with valid parameters
        response = self.client.get(self.url + '?page=1&isfinderrorbook=0&keywords=test',
                                   {'username': self.user_username, 'email': self.user_email})

        self.assertEqual(response.status_code, 200)

        # Check JSON response
        json_response = response.json()
        self.assertTrue(json_response['status'])
        self.assertEqual(json_response['msg'], '获取答题记录信息成功!')
        self.assertIn('data', json_response)
        self.assertEqual(len(json_response['data']), 1)  # Assuming two mock records were returned

        # Optionally, check specific fields in the data returned
        self.assertEqual(json_response['data'][0]['question_content'], 'What is 2+2?')