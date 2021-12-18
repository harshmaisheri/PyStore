from rest_framework import serializers

from store.models import Product, Collection, Review


class CollectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']
        
    product_count = serializers.IntegerField(read_only=True)
        

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'description', 'inventory', 'unit_price', 'tax', 'price_with_tax', 'collection']
    
    tax = serializers.SerializerMethodField(method_name='calculate_tax')
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax_with_price')
    
    @staticmethod
    def calculate_tax(product: Product):
        return product.unit_price * 5 / 100
    
    def calculate_tax_with_price(self, product: Product):
        return self.calculate_tax(product) + product.unit_price


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']
        
    def create(self, validate_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validate_data)
