from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    reviews_given = serializers.SerializerMethodField()

    def get_reviews_given(self, obj):
        return obj.reviews.count()

    class Meta:
        model  = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone', 'role', 'is_verified', 'is_staff', 'profile_picture', 'created_at',
            'reviews_given'
        ]
        read_only_fields = ['id', 'is_verified', 'is_staff', 'created_at', 'reviews_given']


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'phone', 'role', 'password', 'password2'
        ]

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with that email already exists.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        role = validated_data.get('role', 'customer')
        # Always activate the account immediately (no email verification required)
        user = User(
            **validated_data,
            is_active=True,
            is_verified=True,
        )
        user.set_password(password)
        user.save()

        # Auto-create a pending ServiceProvider profile so FK relations work.
        # The provider must complete their profile via the onboarding page.
        if role == 'provider':
            from services.models import ServiceProvider
            ServiceProvider.objects.get_or_create(
                user=user,
                defaults={
                    'business_name': f"{user.first_name or user.username}'s Service",
                    'phone':   user.phone or '',
                    'email':   user.email,
                    'address': 'To be updated',
                    'city':    'To be updated',
                    'state':   'To be updated',
                    'pincode': '000000',
                    'status':  'pending',
                }
            )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Accepts either username OR email in the 'username' field.
    Works regardless of what USERNAME_FIELD is set to on the model.
    """
    # We accept a field called 'username' from the client
    username_field = 'username'

    def validate(self, attrs):
        login_input = attrs.get('username', '').strip()
        password    = attrs.get('password', '')

        # Try to find user by username first, then by email
        user = None
        try:
            user_obj = User.objects.get(username__iexact=login_input)
            # Django ModelBackend authenticates via USERNAME_FIELD which is 'email'
            user = authenticate(
                request=self.context.get('request'),
                email=user_obj.email,
                password=password,
            )
        except User.DoesNotExist:
            pass

        if user is None:
            # Try by email directly
            try:
                user_obj = User.objects.get(email__iexact=login_input)
                user = authenticate(
                    request=self.context.get('request'),
                    email=user_obj.email,
                    password=password,
                )
            except User.DoesNotExist:
                pass

        if user is None:
            raise serializers.ValidationError(
                {'detail': 'No active account found with the given credentials.'}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {'detail': 'This account has been deactivated.'}
            )

        # Generate tokens
        refresh = self.get_token(user)
        data = {
            'refresh': str(refresh),
            'access':  str(refresh.access_token),
            'user':    UserSerializer(user).data,
        }
        return data
