from ..models import User
from ..views.adminsite import setError, setSuccess


class UserService:

    @staticmethod
    def select_user(username,email):
        users=User.objects.filter(is_delete=False, username=username,
                                  email=email)
        return users
