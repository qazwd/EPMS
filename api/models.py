from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from decimal import Decimal


class UsersInfo(models.Model):
    '''
    用户信息模型
    '''

    # 员工类型
    STAFF_TYPE_CHOICES = [
        ('管理人员', '管理人员'),
        ('实施人员', '实施人员'),
    ]
    # 员工状态
    STAFF_STATUS_CHOICES = [
        ('正常', '正常'),
        ('忙碌', '忙碌'),
        ('离线', '离线'),
        ('禁用', '禁用'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='UsersInfo', verbose_name="用户")
    phone = models.CharField(max_length=11, blank=True, verbose_name="手机号码")
    department = models.CharField(max_length=100, blank=True, verbose_name="部门")
    staff_type = models.CharField(max_length=100, blank=True, choices=STAFF_TYPE_CHOICES, verbose_name="员工类型")
    position = models.CharField(max_length=100, blank=True, verbose_name="职位")
    status = models.CharField(max_length=100, blank=True, choices=STAFF_STATUS_CHOICES, verbose_name="状态")
    avatar = models.CharField(max_length=10, default='头像', verbose_name="头像")
    # avatar = models.ImageField(upload_to='avatar/', default='avatar/default.png', blank=True, verbose_name="头像")

    def __str__(self):
        '''
        返回用户名
        '''
        return self.user.username
    
    class Meta:
        '''
         元数据类
        '''
        verbose_name = "用户资料"
        verbose_name_plural = "用户资料"

class Projects(models.Model):
    '''
    项目模型
    '''

    # 项目状态
    STATUS_CHOICES = [
        # ('立项', '立项'),
        # ('设计', '设计'),
        # ('开发', '开发'),
        # ('部署', '部署'),
        # ('测试', '测试'),
        # ('初验', '初验'),
        # ('验收', '验收'),
        ('未开发', '未开发'),
        ('开发中', '开发中'),
        ('已完成', '已完成'),
        ('已验收', '已验收'),
    ]

    project_number = models.CharField(max_length=30, null=False, blank=False, verbose_name="项目编号")
    project_name = models.CharField(max_length=50,  null=False, blank=False, verbose_name="项目名称")
    customer_name = models.CharField(max_length=200, null=False, blank=False, verbose_name="客户名称")
    customer_address = models.CharField(max_length=200, null=True, blank=True, verbose_name="客户地址")
    customer_contact = models.CharField(max_length=100, null=True, blank=True, verbose_name="客户联系人")
    customer_phone = models.CharField(max_length=11, null=True, blank=True, verbose_name="客户联系方式")
    project_amount = models.DecimalField(max_digits=13, decimal_places=2, null=True, blank=True, verbose_name="项目金额")
    required_start = models.DateField(verbose_name="要求开始时间")
    required_end = models.DateField(verbose_name="要求结束时间")
    actual_start = models.DateField(null=True, blank=True, verbose_name="实际开始时间")
    actual_end = models.DateField(null=True, blank=True, verbose_name="实际结束时间")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='未开发', verbose_name="项目状态")
    business_owner = models.CharField(max_length=100, verbose_name="项目商务负责人")
    implementation_owner = models.CharField(max_length=100, verbose_name="项目实施负责人")
    developers = models.TextField(null=True, blank=True, verbose_name="项目开发人员")  # 用逗号分隔
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="项目创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")
    description = models.TextField(null=True, blank=True, verbose_name="项目描述")

    def __str__(self):
        '''
        返回项目名称
        '''
        return self.project_name
    
    class Meta:
        '''
         元数据类
        '''
        verbose_name = "项目"
        verbose_name_plural = "项目"

    def get_developers(self):
        '''
        返回项目开发人员列表
        '''
        if self.developers:
            return self.developers.split(",")
        else:
            return []
        

class ProjectPhases(models.Model):
    '''
    项目阶段模型
    '''

    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name="phases", verbose_name="所属项目")
    phase_name = models.CharField(max_length=100, verbose_name="阶段名称")
    phase_order = models.IntegerField(default=0, verbose_name="阶段顺序")  # 新增字段
    phase_start = models.DateField(null=True, blank=True, verbose_name="阶段开始时间")
    phase_end = models.DateField(null=True, blank=True, verbose_name="阶段结束时间")
    phase_description = models.TextField(null=True, blank=True, verbose_name="阶段描述")

    def __str__(self):
        '''
        返回阶段名称
        '''
        return self.phase_name
    
    def get_phase_duration(self):
        '''
        返回阶段持续时间
        '''
        if self.phase_end and self.phase_start:
            return self.phase_end - self.phase_start
        else:
            return None

    class Meta:
        '''
        元数据类
        '''
        verbose_name = "项目阶段"
        verbose_name_plural = "项目阶段"
        ordering = ['phase_order']  # 按顺序排序


class Reports(models.Model):
    '''
    周报模型
    '''

    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name="reports", verbose_name="所属项目")
    report_title = models.CharField(max_length=100, verbose_name="报告标题")
    report_author = models.CharField(max_length=100, verbose_name="报告作者", default="")
    report_date = models.DateField(verbose_name="报告日期")
    report_content = models.TextField(verbose_name="报告内容")
    plan = models.TextField(verbose_name="下周工作计划")
    issues = models.TextField(blank=True, null=True, verbose_name="遇到的问题")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="最后更新时间")

    def __str__(self):
        '''
        返回周报标题
        '''
        return self.report_title
    
    class Meta:
        '''
        元数据类
        '''
        verbose_name = "周报"
        verbose_name_plural = "周报"


from decimal import Decimal

class Logs(models.Model):
    '''
    日志主表
    '''

    # 日志状态
    STATUS_CHOICES = [
        ('未保存', '未保存'),
        ('已保存', '已保存'),
        ('已提交', '已提交'),
        ('已通过', '已通过'),
        ('未通过', '未通过'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    project = models.ForeignKey('Projects', on_delete=models.CASCADE, verbose_name="项目")
    phase_name = models.CharField(max_length=20, verbose_name="阶段")
    
    # 总工时统计
    # total_work_time = models.DecimalField(max_digits=5, decimal_places=1, default=Decimal('0.0'), verbose_name="总工作时间")
    # total_vacation_time = models.DecimalField(max_digits=5, decimal_places=1, default=Decimal('0.0'), verbose_name="总休假时间")
    # total_overtime = models.DecimalField(max_digits=5, decimal_places=1, default=Decimal('0.0'), verbose_name="总加班时间")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    # # 是否为'提交'
    # status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='未提交', verbose_name="日志状态")
    # # 未通过理由
    # fail_reason = models.CharField(max_length=100, blank=True, null=True, verbose_name="未通过原因")
    
    class Meta:
        verbose_name = "日志主表"
        verbose_name_plural = "日志主表"
        db_table = "api_log"  # 指定表名
    
    # # 重写save方法，计算总工时
    # def save(self, *args, **kwargs):
    #     # 先保存实例以获取主键
    #     super().save(*args, **kwargs)
        
    #     # 只有在有log_dates关联时才计算总工时
    #     if hasattr(self, 'log_dates') and self.log_dates.exists():
    #         total_work_time = Decimal('0.0')
    #         total_vacation_time = Decimal('0.0')
    #         total_overtime = Decimal('0.0')
            
    #         for log in self.log_dates.all():
    #             if log.work_type == '正常工时':
    #                 total_work_time += log.work_time
    #             elif log.work_type == '休假工时':
    #                 total_vacation_time += log.work_time
    #             elif log.work_type == '加班工时':
    #                 total_overtime += log.work_time
    #                 # # 加班工时额外增加8小时正常工时
    #                 # total_work_time += Decimal('8.0')
            
    #         # 避免递归保存，使用update方法
    #         Logs.objects.filter(pk=self.pk).update(
    #             total_work_time=total_work_time,
    #             total_vacation_time=total_vacation_time,
    #             total_overtime=total_overtime
    #         )
    #         # def save(self, *args, **kwargs):
    #         # super().save(*args, **kwargs)



class LogsDate(models.Model):
    '''
    日志日期信息表
    '''

    WORK_TYPE_CHOICES = [
        ('正常工时', '正常工时'),
        ('加班工时', '加班工时'),
        ('休假工时', '休假工时'),
    ]

    STARUS_CHOICES = [
        ('已保存', '已保存'),
        ('已提交', '已提交'),
        ('已通过', '已通过'),
        ('未通过', '未通过'),
    ]
    
    log = models.ForeignKey(Logs, related_name='log_dates', on_delete=models.CASCADE, verbose_name="关联日志")
    date = models.DateField(verbose_name="日期")  # 原需求的date字段应为日期类型
    work_time = models.DecimalField(max_digits=4, decimal_places=1, default=Decimal('0.0'), verbose_name="工作时间")
    work_type = models.CharField(max_length=10, choices=WORK_TYPE_CHOICES, default='正常工时', verbose_name="工作类型")
    work_description = models.TextField(blank=True, verbose_name="工作描述")

    # 日志状态
    log_status = models.CharField(max_length=10, choices=Logs.STATUS_CHOICES, default='已保存', verbose_name="日志状态")
    # 保存时间
    save_time = models.DateTimeField(blank=True, null=True, verbose_name="保存时间")
    # 提交时间
    submit_time = models.DateTimeField(blank=True, null=True, verbose_name="提交时间")
    # 审核时间
    check_time = models.DateTimeField(blank=True, null=True, verbose_name="审核时间")
    # 未通过理由
    fail_cause = models.CharField(max_length=100, blank=True, null=True, verbose_name="未通过原因")
    
    class Meta:
        verbose_name = "日志日期信息表"
        verbose_name_plural = "日志日期信息表"
        db_table = "api_log_date"  # 指定表名
