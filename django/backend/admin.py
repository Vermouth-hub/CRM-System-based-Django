from django.contrib import admin
from .models import (
    Salesman, Company, Order, Product,
    Complaint, CheckItemDict, NewProductFeedback,
    Service, Training, UploadedFile)


admin.site.register(Salesman)
admin.site.register(Company)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Complaint)
admin.site.register(CheckItemDict)
admin.site.register(NewProductFeedback)
admin.site.register(Service)
admin.site.register(Training)
admin.site.register(UploadedFile)

