from rest_framework import serializers
from .models import Company, Order, Complaint, Product

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        depth = 1  # 包含关联对象的详细信息

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = '__all__'
        depth = 1


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ChartDataSerializer(serializers.Serializer):
    total_customer = serializers.IntegerField()
    total_order = serializers.IntegerField()
    total_complaint = serializers.IntegerField()
    total_visit = serializers.IntegerField()
    customer_region = serializers.ListField()
    order_months = serializers.ListField()
    order_counts = serializers.ListField()
