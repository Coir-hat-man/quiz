from io import BytesIO
from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import View

from ..config.config import get_verified_image
from ..config.forms import LoginRegisterForm
from ..models import User, Tag, AnswerRecord, Question, UserActivity
from django.utils import timezone
from django.shortcuts import render

class Index_User_service:
    @staticmethod
    def get_or_create_user_from_session(session):
        curuser = User.objects.filter(email=session.get("email")).first()
        if not curuser:
            curuser = User.objects.create(
            username=session.get("email"),
            email=session.get("email")
        )
        return curuser
    @staticmethod
    def get_user_from_session(request_session):
        user = User.objects.filter(
        is_delete=False,
        email=request_session.get("email", ""),
        username=request_session.get("username", "1")
    ).first()
        return user

class Index_Tag_service:
    @staticmethod
    def get_tag_by_id(tagid):
        tag_info = Tag.objects.filter(nid=tagid, is_delete=False).values('tag', 'nid').first()
        return tag_info


class Index_AnswerRecord_service:
    
    @staticmethod
    def create_answer_record(user, question, answer, is_correct, isInErrorBook=False):
        return AnswerRecord.objects.create(
            user=user,
            question=question,
            answer=answer,
            is_correct=is_correct,
            isInErrorBook=isInErrorBook
        )

    @staticmethod
    def update_answer_record(record_id, answer=None, is_correct=None, isInErrorBook=None):
        answer_record = AnswerRecord.objects.get(record_id=record_id)
        if answer is not None:
            answer_record.answer = answer
        if is_correct is not None:
            answer_record.is_correct = is_correct
        if isInErrorBook is not None:
            answer_record.isInErrorBook = isInErrorBook
        answer_record.save()
        return answer_record

    @staticmethod
    def get_answer_record(record_id):
        try:
            return AnswerRecord.objects.get(record_id=record_id)
        except AnswerRecord.DoesNotExist:
            return None

    @staticmethod
    def delete_answer_record(record_id):
        try:
            AnswerRecord.objects.get(record_id=record_id).delete()
        except AnswerRecord.DoesNotExist:
            pass

    @staticmethod
    def get_records_by_user(user):
        return AnswerRecord.objects.filter(user=user)

    @staticmethod
    def get_records_by_question(question):
        return AnswerRecord.objects.filter(question=question)


class Index_Question_service:

    @staticmethod
    def select_question(content=None,qid=None):
        if content is None and qid is None:
            question = Question.objects.filter(
                is_delete=False
            )
        elif content is None:
            question = Question.objects.filter(
                is_delete=False,
                question_id=qid
            )
        elif qid is None:
            question = Question.objects.filter(
                is_delete=False,
                question_content=content
            )
        else:
            question=Question.objects.filter(
                is_delete=False,
                question_content=content,
                question_id=qid
            )
        return question

    @staticmethod
    def select_relative_question(content,tagname):
        questions=Question.objects.filter(
            question_content__contains=content,
            tag__tag__contains=tagname,
            is_delete=False,
        )
        return questions

class Index_UserActivity_service:
    @staticmethod
    def get_user_activities(user, start_date, end_date):
        user_activities = UserActivity.objects.filter(
        user=user,
        date__range=[start_date, end_date]
    ).order_by('date')
        return user_activities
