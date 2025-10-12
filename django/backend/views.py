from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import FileResponse, JsonResponse, Http404
from django.urls import reverse
from datetime import datetime, timedelta, date
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.db.models import Avg, Q, Count
from django.utils.timezone import make_aware
from .models import (
    Company, Order, Complaint, Product, Salesman, Training, NewProductFeedback, UploadedFile, Service, CheckItemDict)
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from calendar import monthrange
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import UploadedFileForm
import json
import os


def get_month_range(target_date):
    first_day = target_date.replace(day=1)
    if target_date.month == 12:
        next_year = target_date.year + 1
        next_month_first = date(next_year, 1, 1)
    else:
        next_month_first = target_date.replace(month=target_date.month + 1, day=1)
    return first_day, next_month_first


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')   # 已登录，跳转到 dashboard
    else:
        return redirect('login')       # 未登录，跳转到 login


@csrf_exempt
def loginView(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        remember = request.POST.get('remember', False)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            return JsonResponse({
                'success': True,
                'message': '登录成功',
                'redirect_url': reverse('dashboard')
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '用户名或密码错误'
            }, status=400)
    
    return render(request, 'login.html')


@login_required
def logoutView(request):
    logout(request)
    return redirect('login')


@login_required
def dashboardView(request):
    username = request.user.username
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    last_month_start = (start_of_month - timedelta(days=1)).replace(day=1)
    last_month_end = start_of_month - timedelta(days=1)

    total_customers = Company.objects.count()
    last_month_total = Company.objects.filter(create_time__date__lt=start_of_month, create_time__date__gte=last_month_start).count()
    total_growth_rate = ((total_customers - last_month_total) / last_month_total * 100) if last_month_total else 0

    new_customers_this_month = Company.objects.filter(create_time__date__gte=start_of_month).count()
    new_customers_last_month = Company.objects.filter(
        create_time__date__gte=last_month_start,
        create_time__date__lte=last_month_end
    ).count()
    new_growth_rate = ((new_customers_this_month - new_customers_last_month) / new_customers_last_month * 100) if new_customers_last_month else 0

    unresolved_complaints = Complaint.objects.filter(complaint_status=1).count()
    unresolved_last_month = Complaint.objects.filter(
        complaint_status=1,
        create_time__date__gte=last_month_start,
        create_time__date__lte=last_month_end
    ).count()
    complaint_growth_rate = ((unresolved_complaints - unresolved_last_month) / unresolved_last_month * 100) if unresolved_last_month else 0

    avg_satisfaction = Company.objects.aggregate(Avg('satisfaction'))['satisfaction__avg']
    avg_satisfaction = round(avg_satisfaction, 2)
    recent_activities = Training.objects.order_by('-create_time')[:3]
    
    growth_labels = []
    growth_data = []
    for i in range(12):
        target_month = today.month - i
        target_year = today.year
        if target_month <= 0:
            break
        target_date = date(target_year, target_month, 1)
        month_start, month_end = get_month_range(target_date)
        count = Company.objects.filter(
            create_time__gte=month_start,
            create_time__lt=month_end
        ).count()
        growth_labels.append(f"{target_month}月")
        growth_data.append(count)
    growth_data.reverse()
    growth_labels.reverse()
    region_labels = ['北京', '上海', '广州', '深圳', '其他']
    region_data = [Company.objects.filter(region = x).count() for x in region_labels]
    region_data[4] += Company.objects.exclude(region__in=region_labels).count()
    
    context = {
        'username': username,
        'role': "管理员",
        'total_customers': total_customers,
        'total_growth_rate': round(total_growth_rate, 1),
        'new_customers': new_customers_this_month,
        'new_growth_rate': round(new_growth_rate, 1),
        'unresolved_complaints': unresolved_complaints,
        'complaint_growth_rate': round(complaint_growth_rate, 1),
        'satisfaction': avg_satisfaction,
        'recent_activities': recent_activities,
        'growth_labels': growth_labels,
        'growth_data': growth_data,
        'region_labels': region_labels,
        'region_data': region_data,
    }

    return render(request, "dashboard.html", context)

@csrf_exempt
@require_http_methods(["POST"])
def addCompany(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            company_id = data.get('company_id')
            company_name = data.get('company_name')
            
            legal_representative = data.get('legal_representative', None)  # 缺失自动为None
            region = data.get('region', None)
            bank_account = data.get('bank_account', None)
            contact_phone = data.get('contact_phone', None)
            satisfaction = data.get('satisfaction')
            company = Company(
                company_id=company_id,
                company_name=company_name,
                legal_representative=legal_representative,
                region=region,
                bank_account=bank_account,
                contact_phone=contact_phone,
                satisfaction=satisfaction
            )
            company.full_clean()  # 触发模型字段验证（如长度限制、非空校验）
            company.save()  # 保存到数据库
            
            return JsonResponse({
                'status': 'success',
                'message': '公司信息添加成功！',
                'data': {
                    'company_id': company.company_id,
                    'company_name': company.company_name
                }
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'处理失败: {str(e)}'
            }, status=400)
    return JsonResponse({'status': 'error', 'message': '无效的请求方法'}, status=405)


def searchCompany(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': '只允许 GET 请求'}, status=405)
    company_name = request.GET.get('company_name', '').strip()
    company_id = request.GET.get('company_id', '').strip()
    region = request.GET.get('region', '').strip()
    product_id = request.GET.get('product_id', '').strip()
    filters = Q()
    if company_name:
        filters &= Q(company__company_name__icontains=company_name)
    if company_id:
        filters &= Q(company__company_id__icontains=company_id)
    if region:
        if region != 'other':
            filters &= Q(company__region=region)
        else:
            filters &= ~Q(company__region__in=['beijing', 'shanghai', 'guangzhou', 'shenzhen']) & ~Q(company__region='')
    if product_id != "P000":
        filters &= Q(product__product_id__icontains=product_id)
    matching_orders = Order.objects.filter(filters).select_related('company', 'product')
    order_ids = set()
    customer_list = []

    for order in matching_orders:
        oid = order.order_id
        company = order.company
        product = order.product.product_name
        salesman = order.salesman.salesman_name

        if oid not in order_ids:
            order_ids.add(oid)
            customer_list.append({
                'company_id': company.company_id,
                'company_name': company.company_name,
                'region': company.region,
                'contact_people': company.legal_representative,
                'contact_phone': company.contact_phone,
                'product': product,
                'salesman': salesman,
            })
        if len(customer_list) >= 100:
            break

    return JsonResponse({
        'status': 'success',
        'message': f'找到{len(customer_list)}家符合条件的公司',
        'data': customer_list
    })



@login_required
def customerView(request):
    username = request.user.username
    orders = Order.objects.all().order_by('order_id')
    products = Product.objects.all()
    paginator = Paginator(orders, 5)
    page_number = request.GET.get('page', 1)
    try:
        current_page_orders = paginator.page(page_number)
    except PageNotAnInteger:
        current_page_orders = paginator.page(1)
    except EmptyPage:
        current_page_orders = paginator.page(paginator.num_pages)

    context = {
        'username': username,
        'role': "管理员",
        'products': products,
        'orders': current_page_orders,
        'paginator': paginator,
        'current_page': current_page_orders.number,
        'total_pages': paginator.num_pages,
    }
    return render(request, "customer.html", context)


@csrf_exempt
@login_required
def uploadFile(request):
    if request.method == "POST":
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.file_name = request.FILES['file'].name
            uploaded_file.save()
            return JsonResponse({"success": True, "message": "上传成功"})
        else:
            return JsonResponse({"success": False, "message": "表单验证失败", "errors": form.errors})
    return JsonResponse({"success": False, "message": "只支持 POST 请求"})


@csrf_exempt
@login_required
def downloadFile(request, file_id):
    uploaded_file = get_object_or_404(UploadedFile, pk=file_id)
    try:
        response = FileResponse(uploaded_file.file.open("rb"))
        response["Content-Disposition"] = f'attachment; filename="{uploaded_file.file_name}"'
        return response
    except FileNotFoundError:
        raise Http404("文件不存在")
    

@csrf_exempt
@login_required
def deleteFile(request):
    if request.method == "POST":
        file_id = request.POST.get('file_id')
        if not file_id:
            return JsonResponse({"success": False, "message": "缺少文件ID"})
        try:
            f = UploadedFile.objects.get(file_id=file_id)
            f.file.delete()
            f.delete()
            return JsonResponse({"success": True, "message": "删除成功"})
        except UploadedFile.DoesNotExist:
            return JsonResponse({"success": False, "message": "文件不存在"})
    return JsonResponse({"success": False, "message": "只支持 POST 请求"})


@csrf_exempt
@login_required
def addTraining(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            training_id = data.get('training_id')
            training_topic = data.get('training_topic')
            training_type = int(data.get('training_type', 1))  # 默认内部培训
            training_time_str = data.get('training_time')  # 前端传字符串，例如 "2025-10-04 09:30"
            salesman_id = data.get('salesman_id')
            company_id = data.get('company_id')
            training_status = int(data.get('training_status', 0))  # 默认未开始
            if not training_id or not training_topic or not training_time_str:
                return JsonResponse({'status': 'error', 'message': '缺少必填字段'}, status=400)
            try:
                training_time = timezone.datetime.strptime(training_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return JsonResponse({'status': 'error', 'message': '培训时间格式错误'}, status=400)
            salesman = Salesman.objects.get(salesman_id=salesman_id) if training_type == 1 and salesman_id else None
            company = Company.objects.get(company_id=company_id) if training_type == 2 and company_id else None

            training = Training(
                training_id=training_id,
                training_topic=training_topic,
                training_type=training_type,
                training_time=training_time,
                training_status=training_status,
                salesman=salesman,
                company=company,
                create_time=timezone.now()
            )
            training.full_clean()  # 模型字段验证
            training.save()  # 保存到数据库
            return JsonResponse({
                'status': 'success',
                'message': '培训计划添加成功！',
            })
        except Salesman.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '内部培训负责人不存在'}, status=400)
        except Company.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '外部培训单位不存在'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'处理失败: {str(e)}'}, status=400)
    return JsonResponse({'status': 'error', 'message': '无效的请求方法'}, status=405)


@csrf_exempt
@login_required
def supportView(request):
    username = request.user.username
    file = UploadedFile.objects.order_by("-create_time")[:3]
    trainings = Training.objects.all().order_by("training_id")
    paginator = Paginator(trainings, 5)
    page_number = request.GET.get('page', 1)
    salesman = list(Salesman.objects.values("salesman_id", "salesman_name"))
    company = list(Company.objects.values("company_id", "company_name"))
    try:
        current_page_trainings = paginator.page(page_number)
    except PageNotAnInteger:
        current_page_trainings = paginator.page(1)
    except EmptyPage:
        current_page_trainings = paginator.page(paginator.num_pages)
    context = {
        'username': username,
        'role': "管理员",
        'file': file,
        'trainings': current_page_trainings,
        'paginator': paginator,
        'current_page': current_page_trainings.number,
        'total_pages': paginator.num_pages,
        'company': company,
        'salesman': salesman,
    }
    return render(request, "support.html", context)


def get_last_six_months():
    today = date.today()
    months = []
    for i in range(5, -1, -1):  # 从5到0
        month = today.month - i
        year = today.year
        if month <= 0:
            month += 12
            year -= 1
        months.append((year, month))
    return months


@csrf_exempt
@login_required
def createService(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            check_id = data.get("check_id")
            company_id = data.get("company")
            product_id = data.get("product")
            checker_id = data.get("checker")
            check_items_id = data.get("check_items")
            check_time = data.get("check_time")
            cost_time = data.get("cost_time")
            service_status = data.get("service_status", 0)
            if not check_id or not company_id or not product_id or not checker_id or not check_items_id or not check_time:
                return JsonResponse({"status": "error", "message": "缺少必要字段"}, status=400)
            company = Company.objects.get(pk=company_id)
            product = Product.objects.get(pk=product_id)
            checker = Salesman.objects.get(pk=checker_id)
            check_items = CheckItemDict.objects.get(pk=check_items_id)
            if cost_time:
                h, m, s = [int(x) for x in cost_time.split(":")]
                cost_time = timedelta(hours=h, minutes=m, seconds=s)
            else:
                cost_time = timedelta(hours=2)
            service = Service.objects.create(
                check_id=check_id,
                company=company,
                product=product,
                checker=checker,
                check_items=check_items,
                check_time=check_time,   # datetime-local 格式前端要转成 ISO，Django能自动解析
                cost_time=cost_time,
                service_status=service_status,
            )
            service.full_clean()  # 模型字段验证
            service.save()  # 保存到数据库
            return JsonResponse({"status": "success", "message": "服务工单创建成功"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"创建失败：{str(e)}"}, status=500)

    else:
        return JsonResponse({"status": "error", "message": "不支持的请求方法"}, status=405)


@login_required
def serviceView(request):
    username = request.user.username
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    last_month_start = (start_of_month - timedelta(days=1)).replace(day=1)
    last_month_end = start_of_month - timedelta(days=1)

    new_services_this_month = Service.objects.filter(create_time__date__gte=start_of_month).count()
    new_services_last_month = Service.objects.filter(
        create_time__date__gte=last_month_start,
        create_time__date__lte=last_month_end
    ).count()
    new_growth_rate = ((new_services_this_month - new_services_last_month) / new_services_last_month * 100) if new_services_last_month else 0

    waiting_handle_services = Service.objects.filter(service_status=0).count()
    completed_services = Service.objects.filter(service_status =2).count()
    avg_cost_time = Service.objects.aggregate(avg_time=Avg('cost_time'))['avg_time']
    total_avg_hours = avg_cost_time.total_seconds() / 3600
    total_avg_hours = round(total_avg_hours, 1)
    services = Service.objects.all().order_by("check_id")
    paginator = Paginator(services, 3)
    page_number = request.GET.get('page', 1)
    try:
        current_page_services = paginator.page(page_number)
    except PageNotAnInteger:
        current_page_services = paginator.page(1)
    except EmptyPage:
        current_page_services = paginator.page(paginator.num_pages)

    check_items = list(CheckItemDict.objects.all())
    month_data = []
    for i in check_items:
        month_data.append(Service.objects.filter(check_items=i).count())
    month_data[len(check_items) - 1] += Service.objects.exclude(check_items__in=check_items).count()
    months = get_last_six_months()
    completion_rate = []
    avg_hours_per_month = []
    for year, month in months:
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)
        total_services = Service.objects.filter(
            create_time__gte=month_start,
            create_time__lte=month_end
        ).count()
        completed_services_qs = Service.objects.filter(
            create_time__gte=month_start,
            create_time__lte=month_end,
            check_time__gte=month_start,
            check_time__lte=month_end
        )
        completed_services = completed_services_qs.count()
        rate = round((completed_services / total_services) * 100, 1) if total_services else 0
        completion_rate.append(rate)
        if completed_services:
            total_seconds = sum([s.cost_time.total_seconds() for s in completed_services_qs])
            avg_hours = round(total_seconds / 3600 / completed_services, 1)
        else:
            avg_hours = 0
        avg_hours_per_month.append(avg_hours)
    month = [x for y, x in months]
    companies = Company.objects.all()
    products = Product.objects.all()
    salesman = Salesman.objects.all()
    check_items = CheckItemDict.objects.all()

    context = {
        'username': username,
        'role': '管理员',
        'new_services_this_month': new_services_this_month,
        'new_growth_rate': new_growth_rate,
        'waiting_handle_services': waiting_handle_services,
        'completed_services': completed_services,
        'avg_hours': total_avg_hours,
        'services': current_page_services,
        'paginator': paginator,
        'current_page': current_page_services.number,
        'total_pages': paginator.num_pages,
        'month_data': month_data,
        'month': month,
        'completion_rate': completion_rate,
        'avg_hours_per_month': avg_hours_per_month,
        'companies': companies,
        'products': products,
        'salesman': salesman,
        'check_items': check_items,
    }
    return render(request, "service.html", context)


@login_required
@csrf_exempt
def handleComplaint(request, complaint_id):
    if request.method == "POST":
        try:
            complaint = Complaint.objects.get(complaint_id=complaint_id)
            complaint.complaint_status = 2
            complaint.save()
            return JsonResponse({"success": True})
        except Complaint.DoesNotExist:
            return JsonResponse({"success": False, "message": "投诉不存在"})
    return JsonResponse({"success": False, "message": "无效请求"})



@csrf_exempt
@login_required
def createComplaint(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            complaint_id = data.get("complaint_id")
            company_id = data.get("company")
            product_id = data.get("product")
            salesman_id = data.get("salesman")
            complaint_time = data.get("complaint_time")
            complaint_status = data.get("complaint_status", 0)
            complaint_context = data.get("complaint_context")
            company = Company.objects.get(pk=company_id)
            product = Product.objects.get(pk=product_id)
            salesman = Salesman.objects.get(pk=salesman_id)
            complaint = Complaint.objects.create(
                complaint_id=complaint_id,
                company=company,
                product=product,
                salesman=salesman,
                complaint_content=complaint_context,
                complaint_time=complaint_time,
                complaint_status=complaint_status,
            )
            complaint.full_clean()  # 模型字段验证
            complaint.save()  # 保存到数据库
            return JsonResponse({"status": "success", "message": "服务工单创建成功"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"创建失败：{str(e)}"}, status=500)

    else:
        return JsonResponse({"status": "error", "message": "不支持的请求方法"}, status=405)
    


@login_required
def complaintView(request):
    username = request.user.username
    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    complaints_this_month = Complaint.objects.filter(complaint_time__date__gte=start_of_month).count()
    waiting_handle_complaints = Complaint.objects.exclude(complaint_status=2).count()
    handled_complaints = Complaint.objects.filter(complaint_status=2).count()

    complaints = Complaint.objects.all().order_by("complaint_id")
    paginator = Paginator(complaints, 5)
    page_number = request.GET.get('page', 1)
    try:
        current_page_complaints = paginator.page(page_number)
    except PageNotAnInteger:
        current_page_complaints = paginator.page(1)
    except EmptyPage:
        current_page_complaints = paginator.page(paginator.num_pages)


    # 获取全部公司名称
    companies = Company.objects.all()
    products = Product.objects.all()
    salesman = Salesman.objects.all()
    context = {
        'username': username,
        'role': '管理员',
        'complaints_this_month': complaints_this_month,
        'waiting_handle_complaints': waiting_handle_complaints,
        'handled_complaints': handled_complaints,
        'complaints': current_page_complaints,
        'paginator': paginator,
        'current_page': current_page_complaints.number,
        'total_pages': paginator.num_pages,
        'companies': companies,
        'products': products,
        'salesman': salesman,
    }
    return render(request, "complaint.html", context)


@csrf_exempt
def addFeedback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            feedback_id = data.get("feedback_id")
            product_id = data.get("product")
            company_id = data.get("company")
            feedback_type = data.get("feedback_type")
            feedback_time = data.get("feedback_time")
            feedback_content = data.get("feedback_content")
            if not all([feedback_id, product_id, company_id, feedback_type, feedback_time, feedback_content]):
                return JsonResponse({"status": "error", "message": "请填写所有必填项"}, status=400)

            product = Product.objects.get(pk=product_id)
            company = Company.objects.get(pk=company_id)
            feedback_type_map = {"positive": 1, "negative": 2}
            feedback_type_value = feedback_type_map.get(feedback_type)
            if feedback_type_value is None:
                return JsonResponse({"status": "error", "message": "反馈类型错误"}, status=400)
            feedback = NewProductFeedback.objects.create(
                feedback_id=feedback_id,
                product=product,
                company=company,
                feedback_type=feedback_type_value,
                feedback_time=feedback_time,
                feedback_content=feedback_content
            )
            feedback.full_clean()
            feedback.save()
            return JsonResponse({"status": "success", "message": "新品反馈创建成功"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"创建失败：{str(e)}"}, status=500)

    return JsonResponse({"status": "error", "message": "不支持的请求方法"}, status=405)


@login_required
def feedbackView(request):
    username = request.user.username
    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    feedback_this_month = NewProductFeedback.objects.filter(feedback_time__date__gte=start_of_month).count()
    active_feedback = NewProductFeedback.objects.filter(feedback_time__date__gte=start_of_month, feedback_type=1).count()
    negative_feedback = NewProductFeedback.objects.filter(feedback_time__date__gte=start_of_month, feedback_type=2).count()
    feedback = NewProductFeedback.objects.all()
    paginator = Paginator(feedback, 5)
    page_number = request.GET.get('page', 1)
    try:
        current_page_feedbacks = paginator.page(page_number)
    except PageNotAnInteger:
        current_page_feedbacks = paginator.page(1)
    except EmptyPage:
        current_page_feedbacks = paginator.page(paginator.num_pages)

    companies = Company.objects.all()
    products = Product.objects.all()

    products = Product.objects.annotate(
        feedback_count=Count('newproductfeedback')
    ).order_by('product_name')
    product_names = [p.product_name for p in products]
    feedback_counts = [p.feedback_count for p in products]


    months = get_last_six_months()
    active_counts = []
    negative_counts = []
    for year, month in months:
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)
        active_count = NewProductFeedback.objects.filter(
            create_time__gte=month_start,
            create_time__lte=month_end,
            feedback_type=1
        ).count()
        active_counts.append(active_count)
        negative_count = NewProductFeedback.objects.filter(
            create_time__gte=month_start,
            create_time__lte=month_end,
            feedback_type=2
        ).count()
        negative_counts.append(negative_count)
    month = [x for y, x in months]
    context = {
        'username': username,
        'role': "管理员",
        'feedback_this_month': feedback_this_month,
        'active_feedback': active_feedback,
        'negative_feedback': negative_feedback,
        'feedbacks': current_page_feedbacks,
        'paginator': paginator,
        'current_page': current_page_feedbacks.number,
        'total_pages': paginator.num_pages,
        'companies': companies,
        'products': products,
        'product_names': product_names,
        'feedback_counts': feedback_counts,
        'month': month,
        'active_counts': active_counts,
        'negative_counts': negative_counts
    }
    return render(request, "feedback.html", context)