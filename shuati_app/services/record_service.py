from ..models import User, AnswerRecord, Question
from ..views.adminsite import setError, setSuccess
import random


class RecordService:

    @staticmethod
    def fetch_random_question(request):
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

    @staticmethod
    def record_answer(request):
        if not request.session.get("username"):
            return setError("没有登录，无权访问")

        if not request.GET.get("answer"):
            return setError("请提交有效的答案")

        curuser = User.objects.filter(is_delete=False, username=request.session.get("username", ""), email=request.session.get("email", "")).first()
        if not curuser:
            return setError("用户校验失败，无法提交答案")

        q = Question.objects.filter(is_delete=False, question_id=request.GET.get("question_id", "1")).first()
        if not q:
            return setError("question_id不存在")

        if AnswerRecord.objects.filter(is_delete=False, user=curuser, question=q).exists():
            return setError("这道题你已经写过了，无法再次提交")

        AnswerRecord.objects.create(user=curuser, question=q, answer=request.GET.get("answer"), is_correct=(request.GET.get("answer") == q.correct_answer))
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

    @staticmethod
    def fetch_user_record(request):
        if not request.session.get("username") or not request.session.get("email"):
            return setError("没有登录，无权访问")

        if request.session.get("username", "1") != request.GET.get("username", "2") or request.session.get("email", "1") != request.GET.get("email", "2"):
            return setError("用户身份校验未通过，获取题目信息失败")

        user = User.objects.filter(is_delete=False, email=request.session.get("email"), username=request.session.get("username")).first()
        if not user:
            return setError("用户信息核对失败，无法获取数据")

        try:
            page = int(request.GET.get("page"))
            if page <= 0:
                page = 1
        except:
            page = 1

        if request.GET.get("isfinderrorbook", "0") == "1":
            records = AnswerRecord.objects.filter(is_delete=False, user=user, question__question_content__contains=request.GET.get("keywords", ""), isInErrorBook=True).order_by("-create_time")
        else:
            records = AnswerRecord.objects.filter(is_delete=False, user=user, question__question_content__contains=request.GET.get("keywords", "")).order_by("-create_time")

        if not records:
            return setError("没有查询到数据")

        record_data = [
            {
                "is_correct": r.is_correct,
                "create_time": r.create_time,
                "answer": r.answer,
                "question_id": r.question.question_id,
                "question_content": r.question.question_content,
                "correct_answer": r.question.correct_answer,
                "tag": r.question.tag.tag,
                "options": r.question.options,
                "answer_detail": r.question.answer_detail,
                "answer_num": r.question.answer_num(),
                "correctPercent": r.question.correctPercent(),
                "isInErrorBook": r.isInErrorBook,
            }
            for r in records[(page - 1) * 10: page * 10]
        ]

        return setSuccess(
            msg="获取答题记录信息成功!",
            data=record_data,
            len=len(records)
        )

    @staticmethod
    def add_to_error_book(request):
        if not request.session.get("username") or not request.session.get("email"):
            return setError("没有登录，无权访问")

        user = User.objects.filter(is_delete=False, email=request.session.get("email"), username=request.session.get("username")).first()
        if not user:
            return setError("用户身份校验失败，无法获取数据")

        record = AnswerRecord.objects.filter(is_delete=False, user=user, question__question_id=request.GET.get("question_id")).first()
        if not record:
            return setError("警告，异常操作")

        record.isInErrorBook = True
        record.save()
        return setSuccess(msg="加入错题本成功！")

    @staticmethod
    def remove_from_error_book(request):
        if not request.session.get("username") or not request.session.get("email"):
            return setError("没有登录，无权访问")

        user = User.objects.filter(is_delete=False, email=request.session.get("email"), username=request.session.get("username")).first()
        if not user:
            return setError("用户身份校验失败，无法获取数据")

        record = AnswerRecord.objects.filter(is_delete=False, user=user, question__question_id=request.GET.get("question_id")).first()
        if not record:
            return setError("警告，异常操作")

        record.isInErrorBook = False
        record.save()
        return setSuccess("移出错题本成功！")
