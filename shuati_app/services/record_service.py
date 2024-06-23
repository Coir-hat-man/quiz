from ..models import User, AnswerRecord, Question
from ..views.adminsite import setError, setSuccess
import random


class RecordService:

    @staticmethod
    def select_record_by_tag(user,tag_tag,tag_nid):
        answers=AnswerRecord.objects.filter(
            user=user,
            question__tag__tag=tag_tag,
            question__tag__nid=tag_nid
        )
        return answers

    @staticmethod
    def select_record_by_question(user,question):
        answers=AnswerRecord.objects.filter(
            is_delete=False,
            user=user,
            question=question)
        return answers

    @staticmethod
    def select_record_by_question_id(user, question_id):
        answers = AnswerRecord.objects.filter(
            is_delete=False,
            user=user,
            question__question_id=question_id,
        )
        return answers

    @staticmethod
    def select_record_by_keyword(user,keyword,isInErrorBook=None):
        if isInErrorBook is None:
            record = AnswerRecord.objects.filter(
                is_delete=False, user=user,
                question__question_content__contains=keyword
            )
        else:
            record=AnswerRecord.objects.filter(
                is_delete=False, user=user,
                question__question_content__contains=keyword,
                isInErrorBook=True
            )
        return record

    @staticmethod
    def select_answer_by_time(user, time,is_correct=None):
        if is_correct is None:
            answers=AnswerRecord.objects.filter(
                user=user,
                create_time__date=time
            )
        else:
            answers=AnswerRecord.objects.filter(
                user=user,
                create_time__date=time,
                is_correct=is_correct
            )
        return answers


    @staticmethod
    def create_record(user,q,answer,is_correct):
        AnswerRecord.objects.create(user=user, question=q, answer=answer,
                                    is_correct=is_correct)
