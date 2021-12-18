from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import OrderItem, Product, Collection, Review
from .serializers import ProductSerializer, CollectionsSerializer, ReviewSerializer
from rest_framework import status


class ProductViewSet(ModelViewSet):
	serializer_class = ProductSerializer
	
	def get_queryset(self):
		queryset = Product.objects.all()
		collection_id = self.request.query_params.get('collection_id')
		
		if collection_id is not None:
			queryset = queryset.filter(collection_id=collection_id)
		
		return queryset
		
	def get_serializer_context(self):
		return {'context': self.request}
	
	def destroy(self, request, *args, **kwargs):
		if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
			return Response(
				{"error": "Product cannot be delete as it is associated with order items"},
				status=status.HTTP_405_METHOD_NOT_ALLOWED
			)
		return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
	queryset = Collection.objects.annotate(product_count=Count('products')).all()
	serializer_class = CollectionsSerializer
	
	def destroy(self, request, *args, **kwargs):
		collection = get_object_or_404(Collection.objects.annotate(product_count=Count('products')), pk=kwargs['pk'])
		if collection.products.count() > 0:
			return Response(
				{"error": "Collection cannot be deleted because it contains more than one product in it."},
				status=status.HTTP_405_METHOD_NOT_ALLOWED
			)
		return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
	serializer_class = ReviewSerializer
	
	def get_queryset(self):
		return Review.objects.filter(product_id=self.kwargs['product_pk'])
	
	def get_serializer_context(self):
		return {'product_id': self.kwargs['product_pk']}
