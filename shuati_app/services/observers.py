from abc import ABC, abstractmethod
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import UserActivity, AnswerRecord


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
