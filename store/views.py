from django.shortcuts import get_object_or_404
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    UpdateModelMixin,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .filters import ProductFilter
from .models import Cart, CartItem, Customer, OrderItem, Product, Collection, Review
from .pagination import DefaultPagination
from .serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    CartSerializer,
    CollectionSeraializer,
    CustomerSerializer,
    ProductSerializer,
    ReviewSerializer,
    UpdateCartItemSerializer,
)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter
    pagination_class = DefaultPagination

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request: Request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs["pk"]).count() > 0:
            return Response(
                {"error": "Product cannot be deleted becuase it has orderitems"}
            )

        return super().destroy(request, *args, **kwargs)


# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.select_related("collection").all()
#     serializer_class = ProductSerializer

#     def get_serializer_context(self):
#         return {"request": self.request}


# class ProductList(APIView):
#     def get(self, request):
#         queryset = Product.objects.select_related("collection").all()
#         serializer = ProductSerializer(
#             queryset, many=True, context={"request": request}
#         )
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         # if serializer.is_valid():
#         #     serializer.validated_data
#         #     return Response("ok")
#         # else:
#         #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product)

#         if product.orderitems.exists():
#             return Response(
#                 {"error": "You can't delete a product with orderitems"},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED,
#             )
#         product.delete()
#         return Response(
#             {"message": "Product deleted", "data": serializer.data},
#             status=status.HTTP_204_NO_CONTENT,
#         )


# @api_view(["GET", "PUT", "DELETE"])
# def product_detail(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     if request.method == "GET":
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)
#     elif request.method == "PUT":
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == "DELETE":
#         if product.orderitems.exists():
#             return Response(
#                 {"error": "You can't delete a product with orderitems"},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED,
#             )
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count("products")).all()
    serializer_class = CollectionSeraializer

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.exists():
            return Response(
                {"error": "You can't delete a collection with products"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class CollectionList(ListCreateAPIView):
#     queryset = Collection.objects.annotate(products_count=Count("products")).all()
#     serializer_class = CollectionSeraializer


# @api_view(["GET", "POST"])
# def collection_list(request):
#     if request.method == "GET":
#         queryset = Collection.objects.annotate(products_count=Count("products")).all()
#         serializer = CollectionSeraializer(queryset, many=True)
#         return Response(serializer.data)
#     elif request.method == "POST":
#         serializer = CollectionSeraializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Collection.objects.annotate(products_count=Count("products")).all()
#     serializer_class = CollectionSeraializer

#     def delete(self, request, pk):
#         collection = get_object_or_404(Collection, pk=pk)
#         if collection.products.exists():
#             return Response(
#                 {"error": "You can't delete a collection with products"},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED,
#             )
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(["GET", "PUT", "DELETE"])
# def collection_detail(request, pk):
#     collection = get_object_or_404(Collection, pk=pk)
#     if request.method == "GET":
#         serializer = CollectionSeraializer(collection)
#         return Response(serializer.data)
#     elif request.method == "PUT":
#         serializer = CollectionSeraializer(collection, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == "DELETE":
#         if collection.products.exists():
#             return Response(
#                 {"error": "You can't delete a collection with products"},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED,
#             )
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        print(self.kwargs)
        return Review.objects.filter(product__id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}


class CartViewSet(
    CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    queryset = Cart.objects.prefetch_related("items__product").all()
    serializer_class = CartSerializer

    # def retrieve(self, request, *args, **kwargs):
    #     instance = Cart.objects.prefetch_related("items").filter(pk=kwargs["pk"])
    #     return super().retrieve(request, *args, **kwargs)


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self, *args, **kwargs):
        print(self.request.method)
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}

    def get_queryset(self):
        return CartItem.objects.select_related("product").filter(
            cart_id=self.kwargs["cart_pk"]
        )


class CustomerViewSet(
    CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
