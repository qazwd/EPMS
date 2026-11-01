from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from api.models import UsersInfo

@api_view(['POST'])
@csrf_exempt
def user_login(request):
    '''
    用户登录接口
    '''
    username = request.data.get('username')
    password = request.data.get('password')
    
    try:
        # 查找用户
        user = User.objects.get(username=username)

        if user.check_password(password):
            # 获取关联的用户信息
            try:
                userinfo = UsersInfo.objects.get(user_id=user.id)
                # print('currentUserInfo:', userinfo)
                
                # 返回完整的用户信息
                return Response({'status': 'ok', 'message': '验证通过',
                                'user_info': {
                                    # Django内置User模型字段
                                    'id': user.id,
                                    'username': user.username,
                                    'email': user.email,
                                    'name': user.first_name + user.last_name,
                                    'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                                    
                                    # 自定义UsersInfo模型字段
                                    'phone': userinfo.phone,
                                    'department': userinfo.department,
                                    'type': userinfo.staff_type,
                                    'position': userinfo.position,
                                    'status': userinfo.status,
                                    'avatar': userinfo.avatar,
                                }})
            except UsersInfo.DoesNotExist:
                # 处理用户信息不存在的情况
                return Response({
                    'status': 'warning', 
                    'message': '用户存在但信息不完整',
                    'user_info': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'staff_type': '未设置'
                    }
                })
        else:
            return Response({'status': 'error', 'message': '密码错误'}, status=400)
    except User.DoesNotExist:
        return Response({'status': 'error', 'message': '用户不存在'}, status=404)
