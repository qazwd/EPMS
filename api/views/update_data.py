from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import UsersInfo, Projects, Reports, Logs, ProjectPhases
from ..serializers import UsersInfoSerializer, ProjectsSerializer, ReportsSerializer, LogsSerializer, ProjectPhasesSerializer
from django.contrib.auth.models import User


# 更新数据
@api_view(['PATCH'])
def update_data(request):
    """
    处理更新请求
    """

    data = request.data
    # print(f"接收到更新请求：{data}")

    if 'project' in data and data.get('type') == 'project':
        '''更新项目'''
        
        project_data = data.get('project')
        
        if not project_data or 'id' not in project_data:
            return Response(
                {'error': '缺少项目ID或项目数据'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 获取项目实例
            project = Projects.objects.get(id=project_data['id'])
            
            # 更新项目字段（根据实际模型字段调整）
            if 'project_number' in project_data:
                project.project_number = project_data['project_number']
            if 'project_name' in project_data:
                project.project_name = project_data['project_name']
            if 'customer_name' in project_data:
                project.customer_name = project_data['customer_name']
            if 'customer_address' in project_data:
                project.customer_address = project_data['customer_address']
            if 'customer_contact' in project_data:
                project.customer_contact = project_data['customer_contact']
            if 'customer_phone' in project_data:
                project.customer_phone = project_data['customer_phone']
            if 'project_amount' in project_data:
                project.project_amount = project_data['project_amount']
            if 'required_start' in project_data:
                project.required_start = project_data['required_start']
            if 'status' in project_data:
                project.status = project_data['status']
            if 'required_end' in project_data:
                project.required_end = project_data['required_end']
            if 'business_owner' in project_data:
                project.business_owner = project_data['business_owner']
            if 'implementation_owner' in project_data:
                project.implementation_owner = project_data['implementation_owner']
            if 'developers' in project_data:
                project.developers = project_data['developers']
            
            # 处理项目阶段数据
            if 'phases' in project_data:
                # 先删除现有的项目阶段
                ProjectPhases.objects.filter(project=project).delete()
                
                # 创建新的项目阶段
                phases = project_data['phases']
                for index, phase_name in enumerate(phases):
                    ProjectPhases.objects.create(
                        project=project,
                        phase_name=phase_name,
                        phase_order=index + 1  # 按顺序设置阶段顺序
                    )

            
            project.save()
            
            return Response(
                {'message': '项目更新成功', 'project_id': project.id},
                status=status.HTTP_200_OK
            )
            
        except Projects.DoesNotExist:
            return Response(
                {'error': '项目不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'项目更新失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    if 'report' in data and data.get('type') == 'report':
        '''更新周报'''
        
        report_data = data['report']

        if not report_data or 'id' not in report_data:
            return Response(
                {'error': '缺少报告ID或报告数据'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # 获取报告实例
            report = Reports.objects.get(id=report_data['id'])
            
            if 'report_title' in report_data:
                report.report_title = report_data['report_title']
            if 'report_author' in report_data:
                report.report_author = report_data['report_author']
            if 'report_content' in report_data:
                report.report_content = report_data['report_content']
            if 'report_date' in report_data:
                report.report_date = report_data['report_date']
            if 'project_id' in report_data:
                report.project_id = report_data['project_id']
            if 'plan' in report_data:
                report.plan = report_data['plan']
            if 'issues' in report_data:
                report.issues = report_data['issues']

            report.save()
            return Response('success', status=status.HTTP_200_OK)
        except Reports.DoesNotExist:
            return Response(
                {'error': '报告不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'报告更新失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        

    if 'user' in data and data.get('type') == 'user':
        '''更新用户'''
        user_data = data['user']

        if not user_data or 'id' not in user_data:
            return Response(
                {'error': '缺少用户ID或用户数据'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # 获取用户实例
            user = User.objects.get(id=user_data['id'])
            
            # 更新Django内置User模型字段
            if 'name' in user_data:
                user.first_name = user_data['name']
            if 'username' in user_data:
                user.username = user_data['username']
            if 'email' in user_data:
                user.email = user_data['email']
            if 'is_staff' in user_data:
                user.is_staff = user_data['is_staff']
            if 'is_active' in user_data:
                user.is_active = user_data['is_active']
            user.save()
            
            user_info, created = UsersInfo.objects.get_or_create(user=user)
            
            # 更新用户扩展信息(UsersInfo)
            if 'person_type' in user_data:
                user_info.staff_type = user_data['person_type']
            if 'phone' in user_data:
                user_info.phone = user_data['phone']
            if 'email' in user_data:
                user_info.email = user_data['email']
            if 'department' in user_data:
                user_info.department = user_data['department']
            if 'position' in user_data:
                user_info.position = user_data['position']
            user_info.save()
            
            return Response('success', status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'用户更新失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if 'personal' in data and data.get('type') == 'personal':
        '''更新个人信息'''

        user_data = data['personal']
    
        if 'id' not in user_data:
            return Response(
                {'error': '缺少用户ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 获取用户实例
            user = User.objects.get(id=user_data['id'])
            # 获取关联的用户信息实例（假设为一对一关系）
            user_info, created = UsersInfo.objects.get_or_create(user=user)
            
            # 更新Django内置User模型字段
            if 'name' in user_data:
                user.first_name = user_data['name']
            user.save()
            
            # 更新用户扩展信息
            if 'phone' in user_data:
                user_info.phone = user_data['phone']
            if 'email' in user_data:
                user_info.email = user_data['email']
            if 'department' in user_data:
                user_info.department = user_data['department']
            
            user_info.save()
            
            return Response(
                {'message': '个人信息更新成功', 'user_id': user.id},
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'更新失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if 'new_password' in data and data.get('type') == 'password':
        '''更新个人密码'''

        if 'id' not in data or 'current_password' not in data or 'new_password' not in data:
            return Response(
                {'error': '缺少必要字段'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # 验证当前密码
            user = User.objects.get(id=data['id'])
            if not user.check_password(data['current_password']):
                return Response(
                    {'error': '当前密码错误'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                        
            # 更新密码
            user.set_password(data['new_password'])
            user.save()
            return Response(
                {'message': '密码更新成功'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'更新失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    return Response({'error': '无效的更新请求'}, status=status.HTTP_400_BAD_REQUEST)
