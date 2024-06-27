# encoding: utf-8
'''
 @author: Coir-hat-man
 @contact: 1926415776@qq.com
 @wx; l3i700
 @qq; 1926415776
 @file: rank.py
 @time: 2024/6/20/22:45
  '''
import random
from django.shortcuts import render
from django.db.models import Subquery
from django.http import JsonResponse
from .adminsite import setError, setSuccess
from ..config.config import main, get_first_15_chars
from ..models import User,AccuracyVisitor

def ShowRank(request):
    # 判断用户是否登录，否则无权访问此接口
    if (not request.session.get("username")) or (not request.session.get("email")):
        return setError("没有登录，无权访问")

    # 验证用户邮箱是否合格
    # if (request.session.get("username", "1") != request.GET.get("username", "2")) or (
    #         request.session.get("email", "1") != request.GET.get("email", "2")):
    #     return setError("用户身份校验未通过，获取排行榜信息失败")

    # 使用visitor模式获取各个用户的准确率数据
    visitor=AccuracyVisitor()
    records=visitor.rank()
    length=len(records)

    # 返回排行榜数据
    # return setSuccess(
    #     msg="获取排行榜成功",
    #     data=records,
    #     len=length
    # )
    return render(request, 'rank.html', {
        'records': records,
        'length': length
    })




