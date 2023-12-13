from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from . import models
from . import serializers
from rest_framework.permissions import IsAuthenticated, IsAdminUser



from rest_framework.views import APIView
from .serializers import UserManagerSerializers, UserLoginSerializers
from .renderers import UserRenderer
from django.contrib.auth import authenticate


from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    """Registering User"""
    renderer_classes = [UserRenderer]
    def post(self, request):
        serializer = UserManagerSerializers(data=request.data)
        if serializer.is_valid():
            user= serializer.save()
            token = get_tokens_for_user(user)
            return Response({'token':token, 'msg':'Registration Successful'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """Login User"""
    renderer_classes = [UserRenderer]
    def post(self, request):
        serializer = UserLoginSerializers(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response({'token':token, 'msg':'Login Successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'errors':{'non-field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProductView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ListproductsSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


# class CustomerOrdersView(generics.ListAPIView):

#     serializer_class = serializers.OrderSerializers
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return models.Order.objects.filter(user=self.request.user)

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.serializer_class(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

# class AdminOrdersView(generics.ListAPIView, generics.UpdateAPIView):
#     """
#     API view for admin users to view all orders and confirm them.
#     """
#     queryset = models.modelsOrder.objects.all()
#     serializer_class = serializers.OrderSerializers
#     permission_classes = [IsAdminUser]

#     def update(self, request, *args, **kwargs):
#         """
#         Custom implementation for confirming orders.
#         """
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()

#         # Check if the order is already confirmed
#         if instance.status:
#             return Response({'error': 'Order is already confirmed.'}, status=status.HTTP_400_BAD_REQUEST)

#         instance.status = True
#         instance.save()

#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)

#     def list(self, request, *args, **kwargs):
#         """
#         Custom implementation for listing all orders.
#         """
#         queryset = self.get_queryset()
#         serializer = self.serializer_class(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class OrdersView(generics.ListAPIView, generics.UpdateAPIView):
    serializer_class = serializers.OrderSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return models.Order.objects.all()
        else:
            return models.Order.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):

        if not request.user.is_staff:
            return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()


        if instance.status:
            return Response({'error': 'Order is already confirmed.'}, status=status.HTTP_400_BAD_REQUEST)

        instance.status = True
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
