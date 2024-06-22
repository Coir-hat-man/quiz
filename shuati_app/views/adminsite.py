# encoding: utf-8

from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render  # 导出render方法
from django.utils.timezone import localtime  # 导出localtime方法

from ..config.config import get_nid, get_first_15_chars
from ..models import AdminUser, Tag, Question
from  ..services.admin_service import Admin_admin_Service, Admin_question_Service, Admin_tag_Service


def adminlogin(request):
    if request.session.get("admin_username", None):
        return redirect("/shuati_app/adminconsole")
    if request.method == "GET":
        return render(request, "adminsite/adminlogin.html")
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    users=Admin_admin_Service.select_admin(username,password)
    if users.exists():
        request.session["admin_username"] = username
        request.session["is_admin"] = True
        request.session["is_logined"] = True
        return redirect("/shuati_app/adminconsole/")
    return render(request, "adminsite/adminlogin.html", {
        "msg": "用户名或者密码不正确"
    })


def adminconsole(request):
    if not request.session.get("admin_username", None):
        return redirect("/shuati_app/adminlogin?msg=无权访问")
    return render(request, "adminsite/adminconsole.html")


def adminlogout(request):
    request.session.clear()
    return redirect("/shuati_app/adminlogin/?message=退出登录成功！")


def setError(msg):
    return JsonResponse({
        "code": 500,
        "status": False,
        "msg": msg,
        "data": [],
        "len": 0
    }, content_type="application/json")


def setSuccess(msg, data=None, len=0):
    return JsonResponse({
        "code": 200,
        "status": True,
        "msg": msg,
        "data": data,
        "len": len
    }, content_type="application/json")


def admin_addneewtag(request):
    if not request.session.get("admin_username", None):
        return setError("不是管理员，无权操作")
    tagname = request.GET.get("tagname")
    if not tagname:
        return setError("输入的标签名不能为空")
    if Admin_tag_Service.select_tag(tagname=tagname).exists():
        return setError(f"题目分类标签 {tagname} 已经存在，无法继续添加")
    try:
        tag = Admin_tag_Service.create_tag(tagname)
        return setSuccess("新增题目分类标签成功")
    except Exception as error:
        return setError("发生了错误：" + str(error))


def admin_selecttag(request):
    # if not request.session.get("admin_username", None):
    #     return setError("不是管理员，无权操作")
    # 查询的关键字，模糊查询
    tagname = request.GET.get("tagname", "")
    # 查询的页数,每页10条数据，page从1开始
    try:
        page = int(request.GET.get("page"))
        if page <= 0:
            page = 1
    except:
        page = 1
    tags = Admin_tag_Service.select_relative_tag(tagname).order_by('-create_time').all()
    if tags:
        data,length=Admin_tag_Service.create_tag_data(tags,page)
        return setSuccess(
            msg="查询题目标签数据成功",
            data=data,
            len=length
        )
    return setError("没有查询到数据")


def admin_deletetag(request):
    if not request.session.get("admin_username", None):
        return setError("不是管理员，无权操作")
    tagname = request.GET.get("tagname")
    nid = request.GET.get("nid")
    tags = Admin_tag_Service.select_tag(tagname=tagname,nid=nid).first()
    if not tags:
        return setError("没有查询到此数据，无法删除")
    tags.is_delete = True
    tags.save()
    return setSuccess("删除成功")


def admin_edit_tag(request):
    if not request.session.get("admin_username", None):
        return setError("不是管理员，无权操作")
    tagname = request.GET.get("tagname")
    nid = request.GET.get("nid")
    tag = Admin_tag_Service.select_tag(nid=nid).first()
    if not tag:
        return setError("没有查询到此数据，修改失败")
    tag.tag = tagname
    tag.save()
    return setSuccess("修改题目标签成功")


def admin_getAllTagsName(request):
    if not request.session.get("admin_username", None):
        return setError("不是管理员，无权操作")
    tags = Admin_tag_Service.select_tag().order_by('-create_time').all()
    if not tags:
        return setError("没有任何标签，请先去添加标签再新增题目")
    data = []
    for tag in tags:
        data.append({
            "tag": tag.tag,
            "nid": tag.nid
        })
    return setSuccess(
        msg="查询标签成功",
        data=data
    )


def admin_add_question(request):
    if not request.session.get("admin_username", None):
        return setError("不是管理员，无权操作")
    try:
        if Admin_question_Service.select_question(content=request.GET.get("questionContent")).exists():
            return setError("该题目已经存在，不可再次添加，题目问题不可重复")
        question=Admin_question_Service.add_question(items=request.GET.items(),detail=request.GET.get("answer_detail", ""))
        question.save()
        return setSuccess("新增问题信息成功！")
    except Exception as error:
        print(error)
        return setError("系统发生了错误，新增题目信息失败，原因：" + str(error))


def admin_select_question(request):
    if not request.session.get("admin_username", None):
        return setError("不是管理员，无权操作")
    try:
        page = int(request.GET.get("page"))
        if page <= 0:
            page = 1
    except:
        page = 1
    questions=Admin_question_Service.select_relative_question(content=request.GET.get("question_content", "").strip(),
                                                    tagname=request.GET.get("tagname", "")).order_by('-create_time').all()
    if questions:
        qdata,length=Admin_question_Service.create_question_data(questions=questions,page=page)
        return setSuccess(
            msg="查询问题信息成功",
            data=qdata,
            len=length
        )
    return setError("依次此条件，没有查询到题目信息")

def admin_getQuestionByNid(request):
    question_id=request.GET.get("question_id")
    q=Admin_question_Service.select_question(qid=question_id).first()
    if q:
        return setSuccess(
            msg="查询问题成功",
            data=Admin_question_Service.get_question_data(q)
        )
    return setError("没有查询到数据")

def admin_deleteQuestion(request):
    if not request.session.get("admin_username", None):
        return setError("不是管理员，无权操作")
    q = Admin_question_Service.select_question(qid=request.GET.get("question_id","error")).first()
    if q:
        q.is_delete=True
        q.save()
        return setSuccess("删除题目成功！")
    return setError("没有查询到此题目信息，删除失败")