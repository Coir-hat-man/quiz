# encoding: utf-8
'''
 @author: 我不是大佬 
 @contact: 2869210303@qq.com
 @wx; safeseaa
 @qq; 2869210303
 @file: index.py
 @time: 2023/7/1 16:03
  '''

from io import BytesIO
from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import View

from ..config.config import get_verified_image
from ..config.forms import LoginRegisterForm
from ..models import User, Tag, AnswerRecord, Question, UserActivity
from django.utils import timezone
from django.shortcuts import render
from ..services.index_service import Index_User_service, Index_Tag_service, Index_AnswerRecord_service,Index_Question_service,Index_UserActivity_service
def shuati_app_index(request):
    return render(request, "index.html")


class LoginView(View):
    """类视图：处理注册"""

    def get(self, request):
        if request.session.get('info'):  # 如果已经登录，直接跳转到控制台
            return redirect('/shuati_app/')
        """处理GET请求，返回注册页面"""
        return render(request, 'login.html')

    def post(self, request):
        """处理POST请求，实现注册逻辑"""
        if not request.session.get("email", None):
            return render(
                request, 'login.html',
                {
                    "msg": "请点击获取邮箱验证码",
                }
            )
        code = request.POST.get("code", "")
        if code != request.session.get("email_login_code", ""):
            return render(
                request, 'login.html',
                {
                    "msg": "输入的邮箱验证码不正确",
                    "email": request.session.get("email")
                }
            )
        curuser = Index_User_service.get_or_create_user_from_session(request.session)
        request.session["is_logined"] = True
        request.session["email"] = curuser.email
        request.session["username"] = curuser.username
        # 三天免登录
        request.session.set_expiry(60 * 60 * 24 * 3)
        return redirect("/shuati_app/")

def get_captcha(request):
    image, verify = get_verified_image()
    stream = BytesIO()
    image.save(stream, 'png')

    request.session["image_code"] = verify
    # 验证码 60 秒内有效
    request.session.set_expiry(300)
    return HttpResponse(stream.getvalue())


# 退出登录
def logout(request):
    request.session.clear()
    return redirect("/shuati_app/login/?message=退出登录成功！")


def returnErrorPage(request, msg="没有登录，无权访问."):
    return render(request, 'error.html', {
        "msg": msg
    })


def tagdetail(request):
    if not request.session.get("username"):
        return returnErrorPage(request)
    tagid = request.GET.get("tagid")
    tag = Index_Tag_service.get_tag_by_id(tagid)
    if not tag:
        return returnErrorPage(request, "没有查询此标签，无法访问")
    return render(request, "tagdetail.html", {
        "tag_nid": tag["nid"],
        "tag_tag": tag["tag"],
        "user_username": request.session.get("username"),
        "user_email": request.session.get("email")
    })


def record(request):
    if not request.session.get("username"):
        return returnErrorPage(request)
    user = Index_User_service.get_user_from_session(request.session)
    if not user:
        return returnErrorPage(request, msg="用户身份校验失败，无法访问")
        # 获取最近 7 天的用户做题情况
    end_date = timezone.now().date()
    start_date = end_date - timezone.timedelta(days=6)

    user_activities = Index_UserActivity_service.get_user_activities(user, start_date, end_date)

    # 准备数据
    days = [activity.date.day for activity in user_activities]
    months = [activity.date.month for activity in user_activities]
    question_nums = [activity.question_num for activity in user_activities]
    correct_percentages = [activity.correct_percentage for activity in user_activities]
    return render(request, "user/answerrecord.html", {
        "days": days,
        "months":months,
        "question_nums": question_nums,
        "correct_percentages": correct_percentages,
        "user_username": request.session.get("username"),
        "user_email": request.session.get("email"),
        "totalQuestionNum": user.totalQuestionNum(),
        "totalCorrectPercentage": user.totalCorrectPercentage()
    })


def testpage(request):
    return render(request, "testpage.html")

