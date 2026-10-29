from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from ..models import UsersInfo, Projects, Reports, Logs
from ..serializers import UsersInfoSerializer, ProjectsSerializer, ReportsSerializer, LogsSerializer

# 加载数据
@api_view(['GET'])
def load_data(request):
    '''
    加载数据（合并User和UsersInfo表数据）
    '''

    # 获取所有User对象（内置用户表）
    users = User.objects.all()
    # 用于存储合并后的数据
    merged_users = []
    
    for user in users:
        try:
            user_info = user.UsersInfo
        except UsersInfo.DoesNotExist:
            # 处理User没有对应UsersInfo的情况（避免报错）
            user_info = None
        
        # 合并User和UsersInfo的字段（按需选择需要的字段）
        merged_data = {
            # User表字段
            'user_id': user.id,
            'username': user.username,
            'name': user.first_name + user.last_name,
            'email': user.email,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            # UsersInfo表字段（判断是否存在，避免属性错误）
            'phone': user_info.phone if user_info else '',
            'department': user_info.department if user_info else '',
            'staff_type': user_info.staff_type if user_info else '',
            'position': user_info.position if user_info else '',
            'status': user_info.status if user_info else '',
            'avatar': user_info.avatar if user_info else '',
        }
        merged_users.append(merged_data)
    
    # 处理项目、报告、日志数据
    projects = Projects.objects.all()
    reports = Reports.objects.all()
    # logs = Logs.objects.filter(status__in=['已提交', '已通过', '未通过'])
    logs = Logs.objects.all()

    projects_serializer = ProjectsSerializer(projects, many=True)
    # print("项目数据：", projects_serializer.data)
    reports_serializer = ReportsSerializer(reports, many=True)
    # print("周报数据：", reports_serializer.data)
    logs_serializer = LogsSerializer(logs, many=True)
    # print("日志数据：", logs_serializer.data)
    
    return Response({'status': 'ok','message': '数据加载成功',
                     
        'users': merged_users,
        'projects': projects_serializer.data,
        'reports': reports_serializer.data,
        'logs': logs_serializer.data,
    })
