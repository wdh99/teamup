import uuid
import datetime

from django.db import models
from django.utils import timezone
# from django.contrib.auth.models import User
# from django.contrib.gis.db import models as gismodels


class User(models.Model):
    name = models.CharField(max_length=20)
    gender = models.CharField(default='未知', max_length=6) # 男 女 未知
    open_id = models.CharField(max_length=100, unique=True)
    avatar = models.CharField(max_length=100)  # 头像链接
    create_time = models.DateTimeField(default=timezone.now)
    session_key = models.CharField(max_length=200)  # wx.login传过来的

    def __repr__(self) -> str:
        return self.name


class Space(models.Model):
    name = models.CharField(unique=True, max_length=20)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_space')  # Space的对象可以.user_space
    # uuid = models.CharField(default=uuid.uuid4().hex, unique=True, max_length=100)
    users = models.ManyToManyField(User, blank=True)
    create_time = models.DateTimeField(default=timezone.now)

    def __repr__(self) -> str:
        return self.name


class Post(models.Model):
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_post')    #  应该关联openid(为什么?Space需要吗)
    space = models.ForeignKey(Space, on_delete=models.DO_NOTHING, related_name='space_post')
    users = models.ManyToManyField(User, blank=True)  # 活动参与者
    text = models.CharField(max_length=200)  # 帖子文本
    destination_text = models.CharField(max_length=50)
    # duration = models.CharField(max_length=100)  # 活动时间段
    start = models.DateTimeField()
    end = models.DateTimeField()
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    # location = gismodels.PointField()
    # from django.contrib.gis.geos import Point
    # p = Point(x=40.7128, y=-74.0060)
    # # 保存点到数据库
    # location = Location(name='New York City', point=p)
    # location.save()
    join_deadline = models.DateTimeField()  # 默认值：发布时间+1天 9【或者不用默认值，要求用户必须填写】
    quit_deadline = models.DateTimeField()  # 默认值：发布时间+2天
    max_persons = models.IntegerField() 
    price = models.FloatField()
    payment_note = models.CharField(max_length=200) # 收费备注
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class Notify(models.Model):
    text = models.CharField(max_length=300)  # 通知信息