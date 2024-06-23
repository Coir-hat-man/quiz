# encoding: utf-8
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
    def select_user(username,email):
        objects=User.objects.filter(
            username=username,
            email=email
        )
        return objects

class Index_Tag_service:
    @staticmethod
    def select_tag(tagname=None,nid=None):
        if nid is None and tagname is None:
            objects = Tag.objects.filter(
                is_delete=False
            )
        elif nid is None:
            objects = Tag.objects.filter(
                tag=tagname,
                is_delete=False
            )
        elif tagname is None:
            objects = Tag.objects.filter(
                nid=nid,
                is_delete=False
            )
        else:
            objects=Tag.objects.filter(
                tag=tagname,
                nid=nid,
                is_delete=False
            )
        return objects


    @staticmethod
    def select_relative_tag(tagname):
        objects = Tag.objects.filter(
            tag__contains=tagname.strip(),
            is_delete=False
        )
        return objects

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
    def create_user_activity(user, date, question_num, correct_percentage):
        return UserActivity.objects.create(
            user=user,
            date=date,
            question_num=question_num,
            correct_percentage=correct_percentage
        )

    @staticmethod
    def update_user_activity(user_activity_id, question_num=None, correct_percentage=None):
        try:
            user_activity = UserActivity.objects.get(id=user_activity_id)
            if question_num is not None:
                user_activity.question_num = question_num
            if correct_percentage is not None:
                user_activity.correct_percentage = correct_percentage
            user_activity.save()
            return user_activity
        except UserActivity.DoesNotExist:
            return None

    @staticmethod
    def get_user_activity(user_activity_id):
        try:
            return UserActivity.objects.get(id=user_activity_id)
        except UserActivity.DoesNotExist:
            return None

    @staticmethod
    def delete_user_activity(user_activity_id):
        try:
            UserActivity.objects.get(id=user_activity_id).delete()
        except UserActivity.DoesNotExist:
            pass

    @staticmethod
    def get_activities_by_user(user):
        return UserActivity.objects.filter(user=user)

    @staticmethod
    def get_activities_by_date(date):
        return UserActivity.objects.filter(date=date)