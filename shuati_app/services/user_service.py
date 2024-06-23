from ..models import User
from ..views.adminsite import setError, setSuccess


class UserService:

    @staticmethod
    def get_user_detail(request):
        if not request.session.get("username") or not request.session.get("email"):
            return setError("没有登录，无权访问")

        user = User.objects.filter(is_delete=False, email=request.session.get("email"), username=request.session.get("username")).first()
        if not user:
            return setError("用户身份校验失败，无法获取数据")

        return setSuccess(
            msg="获取数据成功！",
            data={
                "username": user.username,
                "email": user.email,
                "detail": user.detail,
                "totalQuestionNum": user.totalQuestionNum(),
                "totalCorrectNum": user.totalCorrectNum(),
                "totalCorrectPercentage": user.totalCorrectPercentage(),
            }
        )
