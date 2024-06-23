from ..models import Tag
from ..models import Question


class QuestionService:

    @staticmethod
    def select_tag():
        objects=Tag.objects.filter(
            is_delete=0
        )
        return objects

    @staticmethod
    def select_question_by_tag(nid,tag):
        q=Question.objects.filter(
            tag__nid=nid,
            tag__tag=tag,
            is_delete=False
        )
        return q

    @staticmethod
    def select_question_by_id(id):
        q=Question.objects.filter(
        is_delete=False, question_id=id)
        return q


    @staticmethod
    def select_question_exclude(nid, tag,answered_questions):
        q=Question.objects.exclude(
            question_id__in=answered_questions). \
            filter(
            is_delete=False,
            tag__tag=tag,
            tag__nid=nid
        )
        return q