from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginView, name='login'),
    path('dashboard/', views.dashboardView, name='dashboard'),

    path('dashboard/customer', views.customerView, name='customer'),
    path('dashboard/customer/add/', views.addCompany, name='add_customer'),
    path('dashboard/customer/search/', views.searchCompany, name='search_company'),

    path('dashboard/support', views.supportView, name='support'),
    path('dashboard/support/upload', views.uploadFile, name='upload_file'),
    path('dashboard/support/download', views.downloadFile, name='download_file'),
    path('dashboard/support/delete', views.deleteFile, name='delete_file'),
    path('dashboard/support/addTraining', views.addTraining, name='add_training'),

    path('dashboard/service', views.serviceView, name='service'),
    path('dashboard/service/add/', views.createService, name='create_service'),

    path('dashboard/complaint', views.complaintView, name='complaint'),
    path("dashboard/complaint/handle/<str:complaint_id>/", views.handleComplaint, name="handle_complaint"),
    path("dashboard/complaint/add/", views.createComplaint, name="create_complaint"),

    path('dashboard/feedback', views.feedbackView, name='feedback'),
    path('dashboard/feedback/add/', views.addFeedback, name='add_feedback'),
    path('logout/', views.logoutView, name='logout'),

]   + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
