from rest_framework import serializers
from .models import Projects, ProjectPhases, Reports, Logs, LogsDate, UsersInfo


class UsersInfoSerializer(serializers.ModelSerializer):
    '''
    用户信息序列化器
    '''
    class Meta:
        model = UsersInfo
        # fields = '__all__'  # 包含所有字段
        # 或者指定特定字段
        fields = ['id', 'phone', 'department', 'staff_type', 'position', 'status', 'avatar', 'user']
        read_only_fields = ['user']



class ProjectPhasesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectPhases
        fields = '__all__'
        # fields = ('id', 'phase_name', 'phase_start', 'phase_end', 'phase_description')


class ProjectsSerializer(serializers.ModelSerializer):
    '''
    项目信息序列化器
    '''
    phases = ProjectPhasesSerializer(many=True, read_only=True)

    class Meta:
        model = Projects
        fields = '__all__'  # 包含所有字段
        # 或者指定特定字段
        # fields = ['id', 'project_name', 'customer_name', 'customer_address', 'customer_contact', 'customer_phone', 'project_amount', 'required_start', 'required_end', 'actual_start', 'actual_end', 'status', 'business_owner', 'implementation_owner', 'description']


class ReportsSerializer(serializers.ModelSerializer):
    '''
    测试报告信息序列化器
    '''
    # 嵌套显示产品信息
    product = ProjectsSerializer(read_only=True)
    
    class Meta:
        model = Reports
        fields = '__all__'  # 包含所有字段
        # 或者指定特定字段
        # fields = ['id', 'report_title', 'report_author', 'report_date', 'report_content', 'plan', 'issues']


class LogsDateSerializer(serializers.ModelSerializer):
    '''
    日志日期信息序列化器
    '''
    class Meta:
        model = LogsDate
        fields = '__all__'  # 包含所有字段
        # 添加read_only_fields，确保log字段在嵌套创建时不会被要求提供
        read_only_fields = ['log']
        # 或者指定特定字段
        # fields = ['id']


from decimal import Decimal

class LogsSerializer(serializers.ModelSerializer):
    log_dates = LogsDateSerializer(many=True, read_only=False)
    
    class Meta:
        model = Logs
        # fields = ['id']
        fields = '__all__'  # 包含所有字段

    
    def create(self, validated_data):
        """
        重写create方法，同时创建日期记录。
        """
        log_dates_data = validated_data.pop('log_dates')
        log = Logs.objects.create(**validated_data)
        
        # 创建所有日期记录
        for date_data in log_dates_data:
            LogsDate.objects.create(log=log, **date_data)
        
        # 重新加载实例以获取关联的log_dates
        log.refresh_from_db()
        
        # 计算并更新总工时
        self.calculate_totals(log)
        
        return log
    
    def update(self, instance, validated_data):
        """
        重写update方法，处理日志日期记录的更新。
        """
        # 处理日志日期数据
        log_dates_data = validated_data.pop('log_dates', [])
        
        # 更新日志主记录
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 处理日期记录
        existing_dates = {str(date.date): date for date in instance.log_dates.all()}
        
        for date_data in log_dates_data:
            date_str = date_data['date']
            if date_str in existing_dates:
                # 更新现有日期记录
                date_obj = existing_dates[date_str]
                for attr, value in date_data.items():
                    setattr(date_obj, attr, value)
                date_obj.save()
            else:
                # 创建新日期记录
                LogsDate.objects.create(log=instance, **date_data)
        
        # 重新计算总工时
        self.calculate_totals(instance)
        
        return instance

    
    # def calculate_totals(self, log):
    #     """计算总工时、总休假时间和总加班时间"""
    #     log_dates = log.log_dates.all()
        
    #     total_work_time = Decimal('0.0')
    #     total_vacation_time = Decimal('0.0')
    #     total_overtime = Decimal('0.0')
        
    #     for date_entry in log_dates:
    #         if date_entry.work_type == '正常工时':
    #             total_work_time += date_entry.work_time
    #         elif date_entry.work_type == '休假工时':
    #             total_vacation_time += date_entry.work_time
    #         elif date_entry.work_type == '加班工时':
    #             total_overtime += date_entry.work_time
    #             # 加班工时额外增加8小时正常工时
    #             total_work_time += Decimal('8.0')
        
    #     # 直接更新字段并保存
    #     log.total_work_time = total_work_time
    #     log.total_vacation_time = total_vacation_time
    #     log.total_overtime = total_overtime
    #     log.save()
