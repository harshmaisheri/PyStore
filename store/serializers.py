from rest_framework import serializers

from store.models import Product, Collection, Review, Cart, CartItem


class CollectionsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Collection
		fields = ['id', 'title', 'product_count']
	
	product_count = serializers.IntegerField(read_only=True)


class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ['id', 'title', 'slug', 'description', 'inventory', 'unit_price', 'tax', 'price_with_tax',
		          'collection']
	
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


class CartProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
	product = CartProductSerializer()
	total_price = serializers.SerializerMethodField()
	
	@staticmethod
	def get_total_price(cart_item: CartItem):
		return cart_item.quantity * cart_item.product.unit_price
	
	class Meta:
		model = CartItem
		fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
	id = serializers.UUIDField(read_only=True)
	items = CartItemSerializer(many=True, read_only=True)
	total_price = serializers.SerializerMethodField()
	
	@staticmethod
	def get_total_price(cart):
		return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
	
	class Meta:
		model = Cart
		fields = ['id', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
	product_id = serializers.IntegerField()
	
	@staticmethod
	def validate_product_id(value):
		if not Product.objects.filter(pk=value).exists():
			raise serializers.ValidationError('No Product with given ID was found!!')
		return value
	
	def save(self, **kwargs):
		cart_id = self.context['cart_id']
		product_id = self.validated_data['product_id']
		quantity = self.validated_data['quantity']
		
		try:
			cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
			cart_item.quantity += quantity
			cart_item.save()
			self.instance = cart_item
		except CartItem.DoesNotExist:
			self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
		
		return self.instance
	
	class Meta:
		model = CartItem
		fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = CartItem
		fields = ['quantity']
