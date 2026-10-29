from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.utils import timezone
from ..models import UsersInfo, Projects, Reports, Logs, LogsDate, ProjectPhases
from ..serializers import UsersInfoSerializer, ProjectsSerializer, ReportsSerializer, LogsSerializer, LogsDateSerializer, ProjectPhasesSerializer

# 创建数据
@api_view(['POST'])
def add_data(request):
    '''
    创建数据
    '''

    data = request.data
    # print("接收到的数据:", data)
    
    # 创建项目
    if 'projectData' in data:
        ''' 创建项目 '''
        project_data = data['projectData']
        # print("接收到的项目数据:", project_data)

        # 提取项目阶段数据
        phases_data = project_data.pop('phases', [])  # 从项目数据中取出阶段数据

        # 创建项目序列化器
        project_serializer = ProjectsSerializer(data=project_data)
        if project_serializer.is_valid():
            # 保存项目
            project = project_serializer.save()
            
            # 创建项目阶段
            for index, phase_name in enumerate(phases_data, start=1):
                phase_data = {
                    'project': project.id,
                    'phase_name': phase_name,
                    'phase_order': index  # 添加阶段顺序
                }
                phase_serializer = ProjectPhasesSerializer(data=phase_data)
                if phase_serializer.is_valid():
                    phase_serializer.save()
                else:
                    # 如果阶段保存失败，删除刚创建的项目并返回错误
                    project.delete()
                    return Response(
                        {'error': f'阶段保存失败: {phase_serializer.errors}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            return Response('success', status=status.HTTP_201_CREATED)
        else:
            return Response({'error': project_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
    # 创建周报
    if 'reportData' in data:
        ''' 创建周报 '''

        report_data = data['reportData']

        # 数据检查
        report_serializer = ReportsSerializer(data=report_data)
        if report_serializer.is_valid():
            report_serializer.save() # 保存到数据库
            return Response('success', status=status.HTTP_201_CREATED)
        else:
            return Response({'error': report_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    
    # 创建日志
    if 'logData' in data:
        ''' 创建 / 更新 日志 '''

        log_data_list = data['logData']
        # print("接收到的日志数据:", log_data_list)

        # 批量创建/更新日志记录
        saved_logs = []
        errors = []
        
        for log_data in log_data_list:
            # 数据验证
            required_log_fields = ['user', 'project', 'phase_name']
            missing_fields = [field for field in required_log_fields if field not in log_data]


            if missing_fields:
                errors.append({'error': f'日志数据缺少必要字段: {", ".join(missing_fields)}', 'data': log_data})
                continue
            
            try:
                user_id = log_data['user']
                project_id = log_data['project']
                phase_name = log_data.get('phase_name')  # phase可能为空
                
                # 获取或创建日志主记录（这部分保持不变）
                log_main, created = Logs.objects.get_or_create(
                    user_id=user_id,
                    project_id=project_id,
                    phase_name=log_data.get('phase_name'),
                    # defaults={
                    #     'total_work_time': 0,
                    #     'total_vacation_time': 0,
                    #     'total_overtime': 0
                    # }
                )
                
                # 处理日期数据：根据logDateId判断是创建还是更新
                for date_data in log_data['log_dates']:
                    date = date_data['date']
                    work_time = date_data.get('work_time', 0)
                    work_type = date_data.get('work_type', '正常工时')
                    work_description = date_data.get('work_description', '')
                    log_status = date_data.get('status', '')
                    log_date_id = date_data.get('logDateId', '').strip()  # 获取logDateId并去除首尾空格
                    
                    if log_date_id:
                        # 如果logDateId不为空，执行更新逻辑
                        try:
                            # 查找对应的日志日期记录，确保属于当前日志主记录
                            log_date = LogsDate.objects.get(
                                id=log_date_id,
                                log=log_main  # 验证所属主记录，确保数据安全
                            )
                            # 更新记录字段，状态设为'未保存'
                            log_date.date = date
                            log_date.work_time = work_time
                            log_date.work_type = work_type
                            log_date.work_description = work_description
                            log_date.log_status = '已保存'  # 设置状态为已保存
                            log_date.save_time = timezone.now()  # 更新保存时间
                            log_date.save()
                        except LogsDate.DoesNotExist:
                            # 记录找不到对应记录的错误
                            errors.append({'error': f'找不到ID为{log_date_id}的日志日期记录', 'data': date_data})
                            continue  # 跳过当前日期数据处理
                    else:
                        # 如果logDateId为空，执行创建新记录逻辑
                        LogsDate.objects.create(
                            log=log_main,
                            date=date,
                            work_time=work_time,
                            work_type=work_type,
                            work_description=work_description,
                            log_status=log_status,
                            save_time=timezone.now(),
                        )

                # 重新计算总工时
                log_main.save()  # 这会触发save方法中的计算逻辑
                
                # 序列化返回
                saved_logs.append(LogsSerializer(instance=log_main).data)
                
            except Exception as e:
                errors.append({'error': f'保存日志失败: {str(e)}', 'data': log_data})
        
        if errors:
            return Response({
                'message': '部分日志保存失败',
                'saved': saved_logs,
                'errors': errors
            }, status=status.HTTP_207_MULTI_STATUS)
        
        return Response({
            'message': '日志保存成功',
            'saved': saved_logs
        }, status=status.HTTP_201_CREATED)
    

    # 提交日志
    if 'submitLogData' in data and data.get('action') == 'submit':
        ''' 
        提交日志（将日志状态改为已提交） 
        '''
        
        submit_log_data_list = data['submitLogData']
        # print("提交日志数据：", submit_log_data_list)

        # 批量更新日志状态
        submitted_logs = []
        errors = []
        
        for log_data in submit_log_data_list:
            # 数据验证：新增logDateId检查
            required_log_fields = ['user', 'project', 'phase_name', 'log_dates']
            missing_fields = [field for field in required_log_fields if field not in log_data]

            if missing_fields:
                errors.append({'error': f'日志数据缺少必要字段: {", ".join(missing_fields)}', 'data': log_data})
                continue
            
            try:
                user_id = log_data['user']
                project_id = log_data['project']
                phase_name = log_data.get('phase_name')  # phase_name可能为空
                
                # 获取日志主记录
                try:
                    log_main = Logs.objects.get(
                        user_id=user_id,
                        project_id=project_id,
                        phase_name=phase_name
                    )
                except Logs.DoesNotExist:
                    errors.append({'error': '找不到对应的日志主记录', 'data': log_data})
                    continue
                
                # 处理日期数据（根据logDateId更新状态）
                for date_data in log_data['log_dates']:
                    # 验证logDateId存在
                    if 'logDateId' not in date_data:
                        raise Exception("日志日期数据缺少logDateId")
                    
                    log_date_id = date_data['logDateId']
                    
                    # 根据logDateId查找对应的日期记录
                    try:
                        log_date = LogsDate.objects.get(
                            id=log_date_id,
                            log=log_main  # 额外验证所属主记录，确保数据安全
                        )
                    except LogsDate.DoesNotExist:
                        raise Exception(f"找不到ID为{log_date_id}的日志日期记录")
                    
                    # 仅更新状态为已提交，不修改其他字段
                    log_date.log_status = '已提交'
                    log_date.submit_time = timezone.now()  # 更新提交时间
                    log_date.save()
            
                # 重新计算总工时并保存（保持原有计算逻辑）
                log_main.save()
                
                # 序列化返回
                submitted_logs.append(LogsSerializer(log_main).data)
                
            except Exception as e:
                errors.append({'error': f'提交日志失败: {str(e)}', 'data': log_data})
        
        if errors:
            return Response({
                'message': '部分日志提交失败',
                'submitted': submitted_logs,
                'errors': errors
            }, status=status.HTTP_207_MULTI_STATUS)
        
        return Response({
            'message': '日志提交成功',
            'submitted': submitted_logs
        }, status=status.HTTP_201_CREATED)
    

    # 撤回提交日志
    if 'withdrawData' in data and data.get('action') == 'withdraw':
        ''' 
        撤回提交日志（将日志状态改为已保存） 
        '''
        
        withdraw_log_data_list = data['withdrawData']['log_dates']
        # print("撤回日志数据：", withdraw_log_data_list)

        # 批量更新日志状态
        withdrawn_logs = []
        errors = []
        
        for log_date_data in withdraw_log_data_list:
            try:
                # 验证logDateId存在
                if 'logDateId' not in log_date_data:
                    raise Exception("日志日期数据缺少logDateId")
                
                log_date_id = log_date_data['logDateId']
                
                # 根据logDateId查找对应的日期记录
                try:
                    log_date = LogsDate.objects.get(id=log_date_id)
                except LogsDate.DoesNotExist:
                    raise Exception(f"找不到ID为{log_date_id}的日志日期记录")
                
                # 更新状态为已保存，不修改其他字段
                log_date.log_status = '已保存'
                log_date.save_time = timezone.now()  # 更新保存时间
                log_date.save()
                
                # 获取对应的主日志记录用于返回
                log_main = log_date.log
                withdrawn_logs.append(LogsSerializer(log_main).data)
                
            except Exception as e:
                errors.append({'error': f'撤回日志失败: {str(e)}', 'data': log_date_data})
        
        if errors:
            return Response({
                'message': '部分日志撤回失败',
                'withdrawn': withdrawn_logs,
                'errors': errors
            }, status=status.HTTP_207_MULTI_STATUS)
        
        return Response({
            'message': '日志撤回成功',
            'withdrawn': withdrawn_logs
        }, status=status.HTTP_200_OK)
    

    # 审批通过日志
    if 'type' in data and data['type'] == 'logs-pass':
        ''' 审批通过多条日志（待完善） '''
        
        log_id = data.get('log_id')
        # print("审批通过日志", log_id)
        
        if not log_id:
            return Response({'error': '缺少日志ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 获取日志记录
            log_main = Logs.objects.get(id=log_id)
            
            # 更新状态为已通过
            log_main.status = '已通过'
            log_main.save()
            
            # 序列化返回
            serialized_log = LogsSerializer(log_main).data
            
            return Response({
                'message': '日志审批通过成功',
                'log': serialized_log
            }, status=status.HTTP_200_OK)
            
        except Logs.DoesNotExist:
            return Response({'error': '找不到对应的日志记录'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'审批失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        

    # 审批拒绝日志
    if 'type' in data and data['type'] == 'logs-reject':
        ''' 审批拒绝多条日志（待完善） '''

        log_id = data.get('log_id')
        reject_reasons = data.get('reject_reasons', '')  # 获取拒绝理由
        # print("审批拒绝日志", log_id, "理由:", reject_reasons)
        
        if not log_id:
            return Response({'error': '缺少日志ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 获取日志记录
            log_main = Logs.objects.get(id=log_id)
            
            # 更新状态为未通过并保存拒绝理由
            log_main.status = '未通过'
            log_main.fail_reason = reject_reasons  # 假设Logs模型有fail_reason字段
            log_main.save()
            
            # 序列化返回
            serialized_log = LogsSerializer(log_main).data
            
            return Response({
                'message': '日志已拒绝',
                'log': serialized_log
            }, status=status.HTTP_200_OK)
            
        except Logs.DoesNotExist:
            return Response({'error': '未找到对应的日志记录'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'处理拒绝操作失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    # 审批通过单个日志
    if 'type' in data and data['type'] == 'log-one-pass':
        ''' 审批通过单条日志 '''

        passData = data.get('passData', {})
        log_date_id = passData.get('log_date_id')
        
        if not log_date_id:
            return Response(
                {'error': '缺少log_date_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 根据根据log_date_id查找对应的日志日期记录
            log_date = LogsDate.objects.get(id=log_date_id)
            # 更新状态为"已通过"
            log_date.log_status = '已通过'
            log_date.check_time = timezone.now()  # 更新审批时间
            log_date.save()
            
            return Response(
                {'message': '日志审批通过成功', 'log_date_id': log_date_id},
                status=status.HTTP_200_OK
            )
        except LogsDate.DoesNotExist:
            return Response(
                {'error': f'找不到ID为{log_date_id}的日志日期记录'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'审批通过失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        

    # 审批拒绝单个日志
    if 'type' in data and data['type'] == 'log-one-reject':
        ''' 审批拒绝单条日志 '''

        rejectData = data.get('rejectData', {})
        log_date_id = rejectData.get('log_date_id')
        reject_reason = rejectData.get('reject_reason', '')  # 获取拒绝理由
        
        if not log_date_id:
            return Response(
                {'error': '缺少log_date_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 仅通过log_date_id查找对应的日志日期记录
            log_date = LogsDate.objects.get(id=log_date_id)
            # 更新状态为"未通过"，并保存拒绝理由（如果模型有该字段）
            log_date.log_status = '未通过'
            if hasattr(log_date, 'fail_cause'):
                log_date.fail_cause = reject_reason
            log_date.check_time = timezone.now()  # 更新审批时间
            log_date.save()
            
            return Response(
                {'message': '日志审批拒绝成功', 'log_date_id': log_date_id},
                status=status.HTTP_200_OK
            )
        except LogsDate.DoesNotExist:
            return Response(
                {'error': f'找不到ID为{log_date_id}的日志日期记录'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'审批拒绝失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    

    # 创建用户
    if 'userData' in data:
        ''' 创建用户（先创建User，再关联UsersInfo） '''

        user_data = data['userData']

        # 1. 验证必要字段
        required_fields = ['username', 'password', 'name']
        missing_fields = [f for f in required_fields if f not in user_data]
        if missing_fields:
            return Response(
                {'error': f'缺少必要字段: {", ".join(missing_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 2. 创建Django内置User实例（映射name到first_name）
            user = User.objects.create_user(
                username=user_data['username'],
                password=user_data['password'],
                first_name=user_data['name']  # 将前端name赋值给User.first_name
            )

            # 3. 准备UsersInfo数据（排除User已处理的字段）
            users_info_data = {
                'user': user,  # 关联刚创建的User
                'phone': user_data.get('phone', ''),
                'staff_type': user_data.get('staff_type', ''),
                # 'position': user_data.get('position', ''),
                'department': user_data.get('department', ''),
                # 其他需要的字段（如department、status等）
            }

            # 4. 创建并保存UsersInfo
            users_info = UsersInfo(**users_info_data)
            users_info.save()

            return Response('success', status=status.HTTP_201_CREATED)

        except Exception as e:
            # 出错时回滚User创建
            if 'user' in locals():
                user.delete()
            return Response(
                {'error': f'创建用户失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    return Response({'error': '无效的创建请求'}, status=status.HTTP_400_BAD_REQUEST)
