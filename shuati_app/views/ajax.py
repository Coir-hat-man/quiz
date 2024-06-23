import random

from django.db.models import Subquery
from django.http import JsonResponse
from .adminsite import setError, setSuccess
from ..config.config import main, get_first_15_chars
from ..models import Tag, User, Question, AnswerRecord, UserActivity
from django.utils import timezone
from datetime import datetime, timedelta
from ..services.user_service import UserService
from ..services.record_service import RecordService
from ..services.tag_service import TagService

from django.db.models.signals import post_save
from django.dispatch import receiver

from abc import ABC, abstractmethod

def getemailcode(request):
    email = request.GET.get("email")
    print("输入的邮箱是；", email)

    code = main(email)
    if code:
        request.session["email"] = email
        request.session['email_login_code'] = code
        request.session.set_expiry(60 * 5)
        data_dict = {"status": True, "msg": "成功向邮箱；" + email + "发送了验证码，请在5分钟内输入正确的验证码完成验证。"}
    else:
        data_dict = {"status": False, "msg": "验证码发送失败，请确认 " + email + " 是否为有效的邮箱地址"}
    return JsonResponse(data_dict)


def getAllTags(request):
    result = TagService.fetch_all_tags()
    return JsonResponse(result)


def getRandomQuestion(request):
    if not request.session.get("username"):
        return setError("没有登录，无权访问")
    # 验证用户邮箱是否合格
    c1 = (request.session.get("username", "1") != request.GET.get("username", "2"))
    c2 = (request.session.get("email", "1") != request.GET.get("email", "2"))
    if c1 or c2:
        return setError("用户身份校验未通过，获取题目信息失败")

    # 判断是否携带标签
    if not Question.objects.filter(
            tag__nid=request.GET.get("tag_nid", ""),
            tag__tag=request.GET.get("tag_tag", ""),
            is_delete=False
    ).exists():
        return setError("此标签暂时没有题目，等待管理员添加中...")

    # 获取用户的邮箱
    email = request.session.get("email")
    # 获取用户对象
    user = User.objects.get(email=email)
    # 使用子查询获取用户已经回答过的题目的id列表
    answered_questions = AnswerRecord.objects.filter(
        user=user,
        question__tag__tag=request.GET.get("tag_tag"),
        question__tag__nid=request.GET.get("tag_nid")
    ).values_list('question__question_id', flat=True)
    q = Question.objects.exclude(
        question_id__in=answered_questions). \
        filter(
        is_delete=False,
        tag__tag=request.GET.get("tag_tag"),
        tag__nid=request.GET.get("tag_nid")
    )
    if not q:
        return setError("此标签的题目已经全部被您刷完啦！去其他的分类看看吧")
    q = q[random.randint(0, len(q) - 1)]
    return setSuccess(
        msg="获取题目成功",
        data={
            "question_id": q.question_id,
            "question_content": q.question_content,
            "options": q.options,
            "create_time": q.create_time
        }
    )



# 提交答案
def submitAnswer(request):
    # 判断用户是否登录，否则无权访问此接口
    if not request.session.get("username"):
        return setError("没有登录，无权访问")
    # 是否提交了答案
    if not request.GET.get("answer"):
        return setError("请提交有效的答案")
    # 校验是否为有效的用户
    curuser = User.objects.filter(is_delete=False, username=request.session.get("username", ""),
                                  email=request.session.get("email", "")).first()
    if not curuser:
        return setError("用户校验失败，无法提交答案")
    # 校验是否为有效的题目
    q = Question.objects.filter(
        is_delete=False, question_id=request.GET.get("question_id", "1")).first()
    if not q:
        return setError("question_id不存在")
    # 判断是否已经写过了这道题目
    if AnswerRecord.objects.filter(
            is_delete=False,
            user=curuser,
            question=q).exists():
        return setError("这道题你已经写过了，无法再次提交")
    # 添加答题记录
    AnswerRecord.objects.create(user=curuser, question=q, answer=request.GET.get("answer"),
                                is_correct=(request.GET.get("answer") == q.correct_answer))
    # 提交成功，返回结果
    return setSuccess(
        msg="提交成功",
        data={
            "result": (request.GET.get("answer") == q.correct_answer),
            "question_id": q.question_id,
            "correct_answer": q.correct_answer,
            "my_answer": request.GET.get("answer"),
            "answer_detail": q.answer_detail,
        }
    )



def getRecord(request):
    result = RecordService.fetch_user_record(request)
    return JsonResponse(result)


def getDetailData(request):
    result = UserService.get_user_detail(request)
    return JsonResponse(result)


def addintoErrorBook(request):
    result = RecordService.add_to_error_book(request)
    return JsonResponse(result)


def removefromErrorBook(request):
    result = RecordService.remove_from_error_book(request)
    return JsonResponse(result)

# 定义抽象观察者类
class Observer(ABC):

    @abstractmethod
    def update(self, instance):
        pass


# 具体观察者类，实现了 Observer 接口
class UserActivityObserver(Observer):

    def update(self, instance, created):
        if created:
            today = instance.create_time.date()
            activity, created = UserActivity.objects.get_or_create(
                user=instance.user,
                date=today
            )
            activity.question_num = AnswerRecord.objects.filter(
                user=instance.user,
                create_time__date=today
            ).count()

            correct_count = AnswerRecord.objects.filter(
                user=instance.user,
                create_time__date=today,
                is_correct=True
            ).count()

            activity.correct_percentage = (correct_count / activity.question_num) * 100 if activity.question_num > 0 else 0.0

            activity.save()


# 创建具体观察者对象
user_activity_observer = UserActivityObserver()


# 注册观察者到信号
@receiver(post_save, sender=AnswerRecord)
def handle_answer_record_save(sender, instance, created, **kwargs):
    user_activity_observer.update(instance, created)




