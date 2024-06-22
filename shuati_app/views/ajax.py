from django.http import JsonResponse
from ..services.user_service import UserService
from ..services.record_service import RecordService
from ..services.tag_service import TagService
from ..config.config import main


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
    result = RecordService.fetch_random_question(request)
    return JsonResponse(result)


def submitAnswer(request):
    result = RecordService.record_answer(request)
    return JsonResponse(result)


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
