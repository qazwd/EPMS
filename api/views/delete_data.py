from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from ..models import UsersInfo, Projects, Reports, Logs, LogsDate
from ..serializers import UsersInfoSerializer, ProjectsSerializer, ReportsSerializer, LogsSerializer
from rest_framework.decorators import api_view

# 删除数据
@api_view(['DELETE'])
def delete_data(request):
    '''
    删除数据
    '''
    data = request.data
    # print('需要删除的数据:', data)
    
    if 'projectId' in data and data.get('type') == 'project':
        '''删除项目'''

        try:
            project = Projects.objects.get(id=data['projectId'])
            project.delete()
            return Response({'message': '项目删除成功'}, status=status.HTTP_200_OK)
        except Projects.DoesNotExist:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    if 'reportIds' in data and data.get('type') == 'report':
        '''批量删除周报'''

        # 获取要删除的周报ID列表
        report_ids = data.get('reportIds')
        
        # 验证ID列表有效性
        if not report_ids or not isinstance(report_ids, list):
            return Response(
                {'error': '缺少有效的周报ID列表（需为非空数组）'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 批量删除：filter查询符合条件的所有周报，delete()返回元组(删除数量, 类型字典)
            deleted_count, _ = Reports.objects.filter(id__in=report_ids).delete()
            
            if deleted_count == 0:
                return Response(
                    {'error': '未找到任何要删除的周报（可能ID不存在）'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {'message': f'成功删除{deleted_count}份周报'},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'error': f'删除失败：{str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        

    if 'logDateIds' in data and data.get('type') == 'log-delete':
        '''删除日志'''
        # 获取要删除的日志ID列表
        log_date_ids = data.get('logDateIds')
        
        # 验证ID列表有效性
        if not log_date_ids or not isinstance(log_date_ids, list):
            return Response(
                {'error': '缺少有效的日志ID列表（需为非空数组）'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 批量删除：filter查询符合条件的所有日志，delete()返回元组(删除数量, 类型字典)
            deleted_count, _ = LogsDate.objects.filter(id__in=log_date_ids).delete()
            
            if deleted_count == 0:
                return Response(
                    {'error': '未找到任何要删除的日志（可能ID不存在）'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {'message': f'成功删除{deleted_count}条日志'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'删除失败：{str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        
    if 'userId' in data and data.get('type') == 'user':
        '''删除用户（先删除UsersInfo，再删除User）'''

        try:
            # 1. 删除UsersInfo
            users_info = UsersInfo.objects.get(user_id=data['userId'])
            users_info.delete()
            
            # 2. 删除User
            user = User.objects.get(id=data['userId'])
            user.delete()
            return Response({'message': '用户删除成功'}, status=status.HTTP_200_OK)
        except UsersInfo.DoesNotExist:
            return Response({'error': '用户信息不存在'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'error': '无效的删除请求'}, status=status.HTTP_400_BAD_REQUEST)
