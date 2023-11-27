- The serializer method can take queryset object, alongside the model object like so:
  ```py
    def products_list(request):
        queryset = Product.objects.all()
        serializer = ProductSerializer(queryset, many=True) # many=True, since we are getting multiple objects
  ```

## POST 
### Validating data
```py
@api_view(['GET', 'POST'])
def products_list(request):
  if request.method == 'POST':
      serializer = ProductSerializer(data=request.data)
      if serializer.is_valid():
          data = serializer.validated_data
          return Response('ok')
```

Cleaner code for this:
```py
@api_view(['GET', 'POST'])
def products_list(request):
  if request.method == 'POST':
      serializer = ProductSerializer(data=request.data)
      serializer.is_valid(raise_exception=True):
      data = serializer.validated_data
      return Response('ok')
```

## Overriding default validation rules
By default, validation matched the Model. But for example, if we have a password1 and password2 and trying to match each other,
we don't have validation for that since there is only 1 password in the model. To compare fields, we  can override the default 
behavior:

```py
class ProductSerializer(serializer.ModelSerializer):
  def validate(self, data):
    if data['password'] != data['confirm_password']:
      return serializers.ValidationError('Passwords do not match')
    return data
```

## Routers
When using viewsets, DRF Routers will generate routers for us, instead of us having to explicitly define the routes.
```py
//urls.py
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register("products", views.ProductViewSet)
router.register("collections", views.CollectionViewSet)

urlpatterns = router.urls // get the generated urls
```

# Authentication - Using Djoser
### JWT vs Token Based

#### - Token
After login, a token is sent to the user. Next time user requests a protected route, the token is sent with the request. A database is required to match this token.

#### - JWT
On the otherhand, JWT doesn't require a database. It has a digital signature in the token itself. When the JWT is sent with the request, the signature is evaulated to see if it is valid, no database required.

### Custom UserCreateSerializer:
- Add custom serializer
- Add customer serializer to the setttings page

```py
DJOSER = {
    "SERIALIZERS": {
        "user_create": "core.serializers.UserCreateSerializer",
    }
}
```

## Extras
#### Why we have both Customers and User tables
User can be anyone, be that admin user or customer. But the customer is a specific type of user, hence separate tables