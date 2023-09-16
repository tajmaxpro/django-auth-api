from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from .serializers import RegisterUserSerializer, LoginUserSerializer, VerifyOTPSerializer
from .models import CustomUser
from django.contrib.auth.hashers import make_password
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .tasks import send_otp_email, generate_and_store_otp
import time
from django.core.cache import cache
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication



# START register_user
@swagger_auto_schema(
    method='post',
    request_body=RegisterUserSerializer,
    operation_summary="*New User Registration*"
)
@api_view(['POST'])
def register_user(request):
    hashed_password = None
    if request.method == 'POST':
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            hashed_password = make_password(serializer.validated_data['password'])
            email = serializer.validated_data['email']
            if CustomUser.objects.filter(email=email).exists():
                return Response({'Error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)
            user = serializer.save(password=hashed_password) 
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# START login_user
@swagger_auto_schema(
    method = 'post',
    request_body = LoginUserSerializer,
    operation_summary="*Login User*"
)
@api_view(['POST'])
def login_user(request):
    serializer = LoginUserSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = CustomUser.objects.filter(email=email).first()
        if user and user.check_password(password):
            generated_test_otp = generate_and_store_otp(user.email)
            # this is for test which will be printed in the terminal
            print('OTP for test:', generated_test_otp)

            send_otp_email(user.email, generated_test_otp)

            request.session['generated_test_otp'] = generated_test_otp
            request.session['user_id'] = user.id 

            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# START verify_otp
@swagger_auto_schema(
    method='post',
    request_body=VerifyOTPSerializer,
    operation_summary="*Verify OTP*"
)
@api_view(['POST'])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    
    if serializer.is_valid():
        input_otp = serializer.validated_data['otp']
        user_id = request.session.get('user_id')

        try:
            user = CustomUser.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        cache_key = f"otp_{user.email}"
        cached_data = cache.get(cache_key)
        if cached_data is None:
            return Response({'error': 'OTP expired or not generated'}, status=status.HTTP_400_BAD_REQUEST)
        print(cached_data)
        cached_otp = cached_data.get('otp')
        cached_timestamp = cached_data.get('timestamp')
        
        if input_otp == cached_otp:
            current_timestamp = int(time.time())
            expiration_time = 120 #seconds
            if current_timestamp - cached_timestamp <= expiration_time:
                token, _ = Token.objects.get_or_create(user=user)
                cache.delete(cache_key)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# START profile_user
@swagger_auto_schema(
    method='get',
    operation_summary="*User Profile*",
    operation_description="""**!** Enter the authentication token you obtained after verifying the OTP into the 'Authorization' field.
    **Example:** Token 'your_token' followed by a space(Token 2a16f6b6cfa1f84b647bba8ea45b3ab11a7b3b93).""",
    manual_parameters=[
        openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token", type=openapi.TYPE_STRING),
    ]
)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile_user(request):
    try:
        user = request.user
        profile_data = {
            'username': user.username,
            'email': user.email
        }
        return Response(profile_data, status=status.HTTP_200_OK)
    except Exception:
        return Response({'error': str(Exception)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


# START update_profile
@swagger_auto_schema(
    methods=['patch'],
    request_body=RegisterUserSerializer,
    operation_summary="*Update User Profile*",
    operation_description="""**!** Enter the authentication token you obtained after verifying the OTP into the 'Authorization' field.
    **Example:** Token 'your_token' followed by a space(Token 2a16f6b6cfa1f84b647bba8ea45b3ab11a7b3b93).""",
    manual_parameters=[
        openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token", type=openapi.TYPE_STRING),
    ]
)
@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    serializer = RegisterUserSerializer(instance=user, data=request.data, partial=True)
    if serializer.is_valid():
        hashed_password = make_password(serializer.validated_data['password'])
        user = serializer.save(password=hashed_password)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        

# START delete_user
@swagger_auto_schema(
    method='delete',
    operation_summary="*Delete User*",
    operation_description="""**!** Enter the authentication token you obtained after verifying the OTP into the 'Authorization' field.
    **Example:** Token 'your_token' followed by a space(Token 2a16f6b6cfa1f84b647bba8ea45b3ab11a7b3b93).""",
    manual_parameters=[
        openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token", type=openapi.TYPE_STRING),
    ]
)
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_user(request):
    user = request.user
    try:
        user.delete()
        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    except Exception:
         return Response({'error': 'An error occurred while deleting the user.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     