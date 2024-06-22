from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render  # 导出render方法
from django.utils.timezone import localtime  # 导出localtime方法

from ..config.config import get_nid, get_first_15_chars
from ..models import AdminUser, Tag, Question

class Admin_admin_Service:
    @staticmethod
    def select_admin(username,password):
        objects=AdminUser.objects.filter(
            username=username,
            password=password
        )
        return objects

class Admin_tag_Service:
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

    @staticmethod
    def create_tag(tagname):
        objects=Tag.objects.create(
            tag=tagname.strip(),
            nid=get_nid()
        )
        return objects

    @staticmethod
    def create_tag_data(tags,page):
        length = len(tags)
        tags = tags[(page - 1) * 10: page * 10]
        data = []
        for tag in tags:
            data.append({
                "tag": tag.tag,
                "create_time": localtime(tag.create_time),
                "nid": tag.nid,
                "question_num": tag.get_question_num()
            })
        return data,length

class Admin_question_Service:

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

    @staticmethod
    def add_question(items,detail):
        question = Question(question_id=get_nid())
        optionsdata = {}
        for key, value in items:
            if key == "questionContent":
                question.question_content = value.strip()
            elif key == "questionCategory":
                question.tag = Tag.objects.filter(
                    tag=value,
                    is_delete=False
                ).first()
            elif key == "correctAnswer":
                question.correct_answer = value
            elif key.startswith("option"):
                optionsdata[key[-1]] = value.strip()
        question.options = optionsdata
        question.answer_detail = detail
        return question

    @staticmethod
    def create_question_data(questions,page):
        length = len(questions)
        questions = questions[(page - 1) * 10: page * 10]
        qdata = []
        for q in questions:
            qdata.append({
                "question_id": q.question_id,
                "question_content": get_first_15_chars(q.question_content),
                "tag": q.tag.tag,
                "answer_num": q.answer_num(),
                "create_time": localtime(q.create_time)
            })
        return qdata,length

    @staticmethod
    def get_question_data(q):
        data = {
            "question_id": q.question_id,
            "question_content": q.question_content,
            "options": q.options,
            "correct_answer": q.correct_answer,
            "tag": q.tag.tag,
            "answer_detail": q.answer_detail,
            "answer_num": q.answer_num(),
            "create_time": localtime(q.create_time)
        }
        return data