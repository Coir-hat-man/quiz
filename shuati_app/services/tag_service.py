from ..models import Tag


class TagService:

    @staticmethod
    def fetch_all_tags():
        tags = Tag.objects.filter(is_delete=0)
        if tags:
            data = [
                {"tag": tag.tag, "create_time": tag.create_time}
                for tag in tags
            ]
            return {
                "code": 200,
                "status": True,
                "msg": "获取题目分类成功",
                "data": data
            }
        return {
            "code": 500,
            "status": False,
            "data": [],
            "msg": "没有查询到数据"
        }
