from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta
from django.utils import timezone
import uuid


# 客户资料管理模块(需要模型：销售员、公司、订单、产品)
class Salesman(models.Model):
    salesman_id = models.CharField(max_length=20, primary_key=True, verbose_name="销售员编码(唯一标识)")
    salesman_name = models.CharField(max_length=20, null=False, verbose_name="销售员姓名")
    contact_info = models.CharField(max_length=20, blank=True, null=True, verbose_name="联系方式(电话)")
    dept = models.CharField(max_length=30, blank=True, null=True, verbose_name="所属部门(如销售一部)")
    create_time = models.DateTimeField(default=timezone.now, verbose_name="创建时间")

    class Meta:
        db_table = "t_salesman"
        verbose_name = "销售员"
        verbose_name_plural = "销售员"

    def to_dict(self):
        return {
            "salesman_id": self.salesman_id,
            "salesman_name": self.salesman_name,
            "contact_info": self.contact_info,
            "dept": self.dept,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }

    
class Company(models.Model):
    company_id = models.CharField(max_length=20, primary_key=True, verbose_name="公司代码")
    company_name = models.CharField(max_length=50, null=False, verbose_name="公司名称")
    legal_representative = models.CharField(max_length=30, blank=True, null=True, verbose_name="法人代表")
    region = models.CharField(max_length=30, blank=True, null=True, verbose_name="所在区域")
    bank_account = models.CharField(max_length=30, blank=True, null=True, verbose_name="银行账号")
    contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="联系电话")
    satisfaction = models.SmallIntegerField(default=5, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name="满意度")
    create_time = models.DateTimeField(default=timezone.now, verbose_name="创建时间")

    class Meta:
        db_table = "t_company"
        verbose_name = "客户单位"
        verbose_name_plural = "客户单位"

    def to_dict(self):
        return {
            "company_id": self.company_id,
            "company_name": self.company_name,
            "legal_representative": self.legal_representative,
            "region": self.region,
            "bank_account": self.bank_account,
            "contact_phone": self.contact_phone,
            'create_time': self.create_time,
        }


class Order(models.Model):
    order_id = models.CharField(max_length=20, primary_key=True, verbose_name="订单编号")
    company = models.ForeignKey(Company, on_delete=models.RESTRICT, verbose_name="关联公司")
    product = models.ForeignKey('Product', on_delete=models.RESTRICT, verbose_name="关联购买产品")
    salesman = models.ForeignKey('Salesman', on_delete=models.RESTRICT, verbose_name="关联负责销售员")
    order_date = models.DateField(null=False, verbose_name="购买日期")
    order_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="订单金额")
    order_status = models.SmallIntegerField(default=1, choices=[(1, '已完成'), (2, '待交付'), (3, '已取消')], verbose_name="订单状态")
    create_time = models.DateTimeField(default=timezone.now, verbose_name="创建时间")

    class Meta:
        db_table = "t_order"
        verbose_name = "订单"
        verbose_name_plural = "订单"

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "company_id": self.company.company_id if self.company else None,
            "company_name": self.company.company_name if self.company else None,
            "product_id": self.product.product_id if self.product else None,
            "product_name": self.product.product_name if self.product else None,
            "salesman_id": self.salesman.salesman_id if self.salesman else None,
            "salesman_name": self.salesman.salesman_name if self.salesman else None,
            "order_date": self.order_date.strftime("%Y-%m-%d"),
            "order_amount": float(self.order_amount) if self.order_amount else None,
            "order_status": ["", "已完成", "待交付", "已取消"][self.order_status],
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
class Product(models.Model):
    product_id = models.CharField(max_length=20, primary_key=True, verbose_name="产品编码")
    product_name = models.CharField(max_length=50, null=False, verbose_name="产品名称")
    product_status = models.SmallIntegerField(default=1, choices=[(1, '常规产品'), (2, '新品')], verbose_name="产品状态")
    product_desc = models.TextField(blank=True, null=True, verbose_name="产品描述")
    create_time = models.DateTimeField(default=timezone.now, verbose_name="创建时间")

    class Meta:
        db_table = "t_product"
        verbose_name = "产品"
        verbose_name_plural = "产品"

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_status": self.product_status,
            "dev_archive_no": self.dev_archive_no,
            "product_desc": self.product_desc,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }

# 客户支持管理模块(模型：培训计划、公司、会议参与人员)
class Training(models.Model):
    training_id = models.CharField(max_length=32, primary_key=True, verbose_name="培训计划编号")
    training_topic = models.CharField(max_length=255, null=False, verbose_name="培训主题")
    training_type = models.IntegerField(null=False, choices=[(1, '内部培训'), (2, '外部培训')], verbose_name="培训类型")
    training_time = models.DateTimeField(null=False, verbose_name="培训时间")
    training_status = models.IntegerField(default=0, choices=[(0, '未开始'), (1, '进行中'), (2, '已结束')], verbose_name="培训状态")
    salesman = models.ForeignKey("Salesman", on_delete=models.RESTRICT, null=True, blank=True, verbose_name="内部培训")
    company = models.ForeignKey("Company",on_delete=models.RESTRICT, null=True, blank=True, verbose_name="外部培训单位")
    create_time = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    class Meta:
        db_table = "training"
        verbose_name = "培训计划"
        verbose_name_plural = "培训计划"

    def to_dict(self):
        return {
            "training_id": self.training_id,
            "training_topic": self.training_topic,
            "training_type": "内部培训" if self.training_type == 1 else "外部培训",
            "training_time": self.training_time.strftime("%Y-%m-%d %H:%M:%S"),
            "training_people": self.salesman if self.training_type == 1 else self.company,
            "training_status_text": ["未开始", "进行中", "已结束"][self.training_status],
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }

# 走访考核表单
class CheckItemDict(models.Model):
    item_id = models.AutoField(primary_key=True, verbose_name="服务细则ID")
    item_name = models.CharField(max_length=50, unique=True, null=False, verbose_name="服务细则名称")

    class Meta:
        db_table = "t_check_item_dict"
        verbose_name = "服务项字典"
        verbose_name_plural = "服务项字典"

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "item_name": self.item_name,
        }
    
class Service(models.Model):
    check_id = models.CharField(max_length=20, primary_key=True, verbose_name="服务单编号")
    company = models.ForeignKey(Company, on_delete=models.RESTRICT, verbose_name="关联客户单位")
    product = models.ForeignKey(Product, on_delete=models.RESTRICT, verbose_name="关联产品")
    checker = models.ForeignKey(Salesman, on_delete=models.RESTRICT, verbose_name="服务人员")
    check_items = models.ForeignKey(CheckItemDict, on_delete=models.CASCADE, verbose_name="服务内容")
    check_time = models.DateTimeField(null=False, verbose_name="服务时间")
    cost_time = models.DurationField(default=timedelta(hours=2), verbose_name="服务时长")
    service_status = models.IntegerField(default=0, choices=[(0, '未开始'), (1, '进行中'), (2, '已完成')], verbose_name="服务状态")
    create_time = models.DateTimeField(default=timezone.now, verbose_name="创建时间")

    class Meta:
        db_table = "t_service"
        verbose_name = "服务质量检查考核单"
        verbose_name_plural = "服务质量检查考核单"

    def to_dict(self):
        return {
            "check_id": self.check_id,
            "company_id": self.company.company_id if self.company else None,
            "company_name": self.company.company_name if self.company else None,
            "product_id": self.product.product_id if self.product else None,
            "product_name": self.product.product_name if self.product else None,
            "check_time": self.check_time.strftime("%Y-%m-%d %H:%M:%S"),
            "checker": self.checker,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    
# 投诉管理系统
class Complaint(models.Model):
    complaint_id = models.CharField(max_length=20, primary_key=True, verbose_name="投诉单编号")
    company = models.ForeignKey(Company, on_delete=models.RESTRICT, verbose_name="关联客户单位")
    product = models.ForeignKey(Product, on_delete=models.RESTRICT, verbose_name="关联产品")
    salesman = models.ForeignKey(Salesman, on_delete=models.RESTRICT, verbose_name="处理人")
    complaint_content = models.TextField(null=False, verbose_name="投诉内容")
    complaint_time = models.DateTimeField(default=datetime.now, null=False, verbose_name="投诉时间")
    complaint_status = models.SmallIntegerField(default=0, choices=[(0, '待处理'), (1, '处理中'), (2, '已完成')], verbose_name="投诉状态")
    create_time = models.DateTimeField(default=timezone.now, verbose_name="创建时间")

    class Meta:
        db_table = "t_complaint"
        verbose_name = "客户投诉"
        verbose_name_plural = "客户投诉"

    def to_dict(self):
        return {
            "complaint_id": self.complaint_id,
            "company_id": self.company.company_id if self.company else None,
            "company_name": self.company.company_name if self.company else None,
            "complaint_content": self.complaint_content,
            "complaint_time": self.complaint_time.strftime("%Y-%m-%d %H:%M:%S"),
            "related_order_id": self.related_order_id,
            "complaint_status": ["待处理", "处理中", "已结案"][self.complaint_status],
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }


# 新品反馈表
class NewProductFeedback(models.Model):
    feedback_id = models.CharField(max_length=20, primary_key=True, verbose_name="新品反馈编号")
    product = models.ForeignKey('Product', on_delete=models.RESTRICT, verbose_name="关联新品")
    company = models.ForeignKey(Company, on_delete=models.RESTRICT, verbose_name="关联反馈客户")
    feedback_type = models.SmallIntegerField(default=1, choices=[(1, '正面反馈'), (2, '负面反馈')], verbose_name="反馈类型")
    feedback_content = models.TextField(blank=True, null=True, verbose_name="反馈内容")
    feedback_time = models.DateTimeField(default=datetime.now, null=False, verbose_name="反馈时间")
    create_time = models.DateTimeField(default=timezone.now, verbose_name="创建时间")

    class Meta:
        db_table = "t_new_product_feedback"
        verbose_name = "新品市场反馈"
        verbose_name_plural = "新品市场反馈"

    def to_dict(self):
        return {
            "feedback_id": self.feedback_id,
            "product_id": self.product.product_id if self.product else None,
            "product_name": self.product.product_name if self.product else None,
            "company_id": self.company.company_id if self.company else None,
            "company_name": self.company.company_name if self.company else None,
            "feedback_type": self.feedback_type,
            "feedback_content": self.feedback_content,
            "feedback_time": self.feedback_time.strftime("%Y-%m-%d %H:%M:%S"),
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    

class UploadedFile(models.Model):
    file_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length = 40, default="技术文档")
    file = models.FileField(upload_to="uploads/")
    description = models.CharField(max_length=100, verbose_name="文档描述")
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "t_file"
        verbose_name = "文件路径"
        verbose_name_plural = "文件路径"


