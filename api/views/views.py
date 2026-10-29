from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from ..models import UsersInfo, Projects, ProjectPhases, Reports, Logs, LogsDate
from ..serializers import UsersInfoSerializer, ProjectsSerializer, ProjectPhasesSerializer, ReportsSerializer, LogsSerializer, LogsDateSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view

class UsersInfoViewSet(viewsets.ModelViewSet):
    '''
    用户信息视图集合
    '''
    queryset = UsersInfo.objects.all()
    serializer_class = UsersInfoSerializer
    # permission_classes = [IsAuthenticated]  # 仅允许认证用户访问

    class Meta:
        '''
        元数据类
        '''
        model = UsersInfo
        fields = '__all__'  # 包含所有字段

    def create(self, request):
        """
        创建用户，即创建用户的同时创建用户账户，并将用户账户信息保存到用户信息表中
        处理完整的创建请求流程，包括更详细的错误提示
        """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=201)
        except ValueError as ve:
            # 捕获在perform_create等环节抛出的ValueError，返回带有详细错误信息的响应
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 捕获其他未知异常，同样返回错误提示响应
            return Response({"error": "未知错误，请联系管理员：{}".format(str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        """
        创建用户，即创建用户的同时创建用户账户，并将用户账户信息保存到用户信息表中
        同时完善两者之间的关联及数据传递
        """
        try:
            # 从序列化器验证后的数据中提取创建User实例所需的关键信息（假设用户名和密码是必要的）
            username=serializer.validated_data['username']
            password=serializer.validated_data['password']
            if not username or not password:
                raise ValueError("用户名和密码是必填项，请检查输入数据")
            # 创建User对象，同时进行密码加密等必要操作
            user = User.objects.create_user(username=username, password=password)
            # 获取关联的UsersInfo序列化器实例
            users_info_serializer = UsersInfoSerializer(data=serializer.validated_data)
            if users_info_serializer.is_valid():
                # 创建UsersInfo实例，但不保存到数据库（避免重复保存等问题）
                users_info = users_info_serializer.save(commit=False)
                # 将创建的User实例关联到UsersInfo实例的user字段
                users_info.user = user
                # print(users_info)
                # 保存UsersInfo实例到数据库，完成关联数据的持久化存储
                users_info.save()
                # 将关联好的UsersInfo实例赋值给序列化器的instance属性，方便后续序列化返回
                serializer.instance = users_info
            else:
                raise ValueError("用户信息表数据验证失败，请检查输入数据格式：{}".format(users_info_serializer.errors))
        except Exception as e:
            # 捕获可能出现的其他异常，返回更友好的错误提示信息给客户端
            raise ValueError("创建用户时出现错误：{}".format(str(e)))
    

class ProjectsViewSet(viewsets.ModelViewSet):
    '''
    项目视图集合
    '''
    queryset = Projects.objects.all()
    serializer_class = ProjectsSerializer
    # permission_classes = [IsAuthenticated]  # 仅允许认证用户访问


class ProjectPhasesViewSet(viewsets.ModelViewSet):
    '''
    项目阶段视图集合
    '''
    queryset = ProjectPhases.objects.all()
    serializer_class = ProjectPhasesSerializer
    # permission_classes = [IsAuthenticated]  # 仅允许认证用户访问


class ReportsViewSet(viewsets.ModelViewSet):
    '''
    报告视图集合
    '''
    queryset = Reports.objects.all()
    serializer_class = ReportsSerializer
    # permission_classes = [IsAuthenticated]  # 仅允许认证用户访问


class LogsViewSet(viewsets.ModelViewSet):
    '''
    日志视图集合
    '''
    
    queryset = Logs.objects.all().prefetch_related('log_dates')  # 预加载关联数据
    serializer_class = LogsSerializer
    # permission_classes = [IsAuthenticated]  # 仅允许认证用户访问
