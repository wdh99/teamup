import hashlib,json
from typing import Any 

import requests
from django.http import HttpRequest, JsonResponse, HttpResponse, QueryDict
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view,action

from .models import User,Space,Post
from .serializers import *

        
# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# ViewSets define the view behavior.
class SpaceViewSet(viewsets.ModelViewSet):
    queryset = Space.objects.all()
    serializer_class = SpaceSerializer

    def get_queryset(self):
        owner = self.request.query_params.get('owner', None)
        user_id = self.request.query_params.get('user_id', None)
        # 获取用户创建的空间
        if owner is not None:
            queryset = Space.objects.filter(owner=owner).order_by('id')
        # 获取用户有关的空间(加入和创建的)
        elif user_id is not None:
            queryset = Space.objects.filter(users=user_id).order_by('id')
        else:
            queryset = super().get_queryset()
        return queryset

    @action(detail=True, methods=['post'])
    def add_user_to_space(self, request, *args, **kwargs):
        data = request.data
        space = self.get_object()
        user = User.objects.filter(pk=data['user_id']).first()
        if user:
            space.users.add(user)
        return Response({'errMsg': 'request:ok'})

    @action(detail=True, methods=['post'])
    def delete_user_from_space(self, request, *args, **kwargs):
        data = request.data
        space = self.get_object()
        if space.owner.id == data['user_id']:
            return Response({'msg': 'cant not delete yourself'}, status=403)
        user = User.objects.filter(pk=data['user_id']).first()
        if user:
            space.users.remove(user)
        return Response({'errMsg': 'request:ok'})


# ViewSets define the view behavior.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = None

    def get_serializer_class(self): # 重写了基类里面的get_serializer_class方法,这是固定写法
        if self.request.method in ['PUT','POST','PATCH']:
            serializers_class = PostSerializerForPOST
        elif self.request.method == 'GET':
            serializers_class = PostSerializerForGET
        return serializers_class

    def get_queryset(self):
        owner = self.request.query_params.get('owner', None)
        space_id = self.request.query_params.get('space_id', None)
        user_id = self.request.query_params.get('user_id', None)
        # 获取用户创建的活动、帖子
        if owner is not None:
            queryset = Post.objects.filter(owner=owner).order_by('-create_time')
        # 获取用户有关的活动
        elif user_id is not None:
            queryset = Post.objects.filter(users=user_id).order_by('-create_time')
        # 获取某空间下的活动
        elif space_id is not None:
            queryset = Post.objects.filter(space=space_id).order_by('-create_time')
        else:
            queryset = super().get_queryset()
        return queryset

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @action(detail=True,methods=['post'])
    def add_user_to_post(self, request, pk=None):
        data = request.data
        post = self.get_object()
        user = User.objects.filter(pk=data['user_id']).first()
        if user:
            post.users.add(user)
        return Response({'errMsg': 'request:ok'})
    
    @action(detail=True,methods=['post'])
    def delete_user_from_post(self, request, pk=None):
        data = request.data
        post = self.get_object()
        if post.owner.id == data['user_id']:
            # 自己不能退出自己创建的帖子
            return Response({'msg': 'cant not delete yourself'}, status=403)

        user = User.objects.filter(pk=data['user_id'])
        if user:
            post.users.remove(user)

        return Response({'msg': 'ok'}, status=200)
        


# @api_view(['GET'])
# def add_user_to_post(request):
#     return Response({"message": "Hello, world!"})


# @api_view(['DELETE'])
# def delete_user_from_post(request):
#     return Response({"message": "Hello, world!"})


def check_signature(signature,timestamp,nonce):
    token = 'wechatpush'
    tmpArr = [token, timestamp, nonce]
    tmpArr.sort()
    tmpStr = "".join(tmpArr)
    tmpStr = hashlib.sha1(tmpStr.encode()).hexdigest()

    if tmpStr == signature:
        return True
    else:
        return False
    

# 微信消息推送
def push(r:HttpRequest):
    signature = r.GET.get('signature')
    timestamp = r.GET.get('timestamp')
    nonce = r.GET.get('nonce')  # 随机数
    echostr = r.GET.get('echostr')  # 随机字符串
    print(signature)
    print(timestamp)
    print(nonce)
    print(echostr)

    if check_signature(signature,timestamp,nonce):
        return HttpResponse(echostr)



@api_view(['GET','POST'])
def login(r:HttpRequest):
    res = {'msg':'', 'code':-1}

    # 判断token是否有效， 不用一登陆就存一个token
    t = r.GET.get('token')
    openid = cache.get(t)
    if openid:
        res['code'] = 2
        user = User.objects.get(open_id=openid)
        res['user'] = UserSerializer(user).data
        res['msg'] = 'token没过期'
        return JsonResponse(res)
    
    user_code = r.GET.get('code')
    if not user_code:
        res['msg'] = '请求缺少code'
        return JsonResponse(res)

    # code 2 session
    App_id = 'wx580677cbb6245c9d'
    App_secret = '9b555b6a2aaa17ffb3cbd499e1b21ba3'
    api_url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code'
    get_url = api_url.format(App_id,App_secret,user_code)
    rr = requests.get(get_url,timeout=5)
    json_data = rr.json()
    
    openid:str = json_data.get('openid','')
    session_key:str = json_data.get('session_key','')
    unionid:str = json_data.get('unionid','')
    errmsg:str = json_data.get('errmsg','')

    if 'errcode' in rr:
        errcode:int = json_data['errcode']
        if errcode == 40029:
            res['msg'] = 'js_code无效'
        elif errcode == 45011:
            res['msg'] = 'API 调用太频繁，请稍候再试'
        elif errcode == 40226:
            res['msg'] = '高风险等级用户，小程序登录拦截。'
        elif errcode == 40226:
            res['msg'] = '系统繁忙，此时请开发者稍候再试。'
        return JsonResponse(res)

    # 校验用户, 不存在则创建
    # User.objects.get_or_create(open_id=openid)
    try:
        user = User.objects.get(open_id=openid)
    except:
        user = User.objects.create(
            name = '微信用户',
            avatar = '/images/def_avatar.png',
            open_id = openid,
        )
    user.session_key = session_key
    user.save()
    user_str = json.dumps(UserSerializer(user).data)

    # 保存token
    sha = hashlib.sha1()
    sha.update(openid.encode())
    sha.update(session_key.encode())
    token = sha.hexdigest()
    cache.set(token, openid, timeout=2*3600)  # 2小时过期
    
    res['code'] = 1
    res['token'] = token
    res['user'] = json.loads(user_str)
    res['msg'] = '登录成功'
    return JsonResponse(res)


def check_token(token):
    t = cache.get(token)  # 2小时过期
    if t:
        return True
    else:
        return False
    

# @api_view(['GET', 'POST'])
# def space(r:HttpRequest):
#     if r.method == 'GET':
#         space = Space.objects.all()
#         serializer = SpaceSerializer(space)
#         return JsonResponse(serializer.data, safe=False)
#     elif r.method == 'POST':
#         data = JSONParser().parse(r)
#         serializer = SpaceSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data, status=201)
#         return JsonResponse(serializer.errors, status=400)
    

# def space_detail(r:HttpRequest,pk):
#     try:
#         space = Space.objects.get(pk=pk)
#     except Space.DoesNotExist:
#         return HttpResponse(status=404)
    
#     if r.method == 'GET':
#         space = Space.objects.all()
#         serializer = SpaceSerializer(space)
#         return JsonResponse(serializer.data, safe=False)
    
#     elif r.method == 'PUT':
#         data = JSONParser().parse(r)
#         serializer = SpaceSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data)
#         return JsonResponse(serializer.errors, status=400)
    
#     elif r.method == 'DELETE':
#         space.delete()
#         return HttpResponse(status=204)
    

# def user(r:HttpRequest):
#     pass


# def post(r:HttpRequest):
#     if r.method == 'GET':
#         r.GET.get('')
#     if r.method == 'POST':
#         r.POST.get('')
#     if r.method == 'PUT':
#         params = QueryDict(r.body)
#         # print(params)
#         params.get('')
#     if r.method == 'DELETE':
#         params = QueryDict(r.body)
    


def get_spaces_of_user(r:HttpRequest):
    pass

