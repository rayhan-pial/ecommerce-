from django.urls import path, include
from . views import UserRegistrationView, UserLoginView, ProductView,OrdersView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('products/', ProductView.as_view(), name='product-list-create'),
    path('orders/', OrdersView.as_view(), name='orders'),

]
