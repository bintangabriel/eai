from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth import authenticate

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'no_telp', 'password', 'profile_picture')

class UpdateUserProfileDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'no_telp')

class UpdateUserProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'profile_picture')

class UpdateUserProfilePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'password')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'no_telp', 'password', 'profile_picture', 'is_active')
        extra_kwargs = {'password':{'write_only': True}}

    def create(self, validated_data):
        validated_data['is_active'] = False
        user = UserProfile.objects.create_user(**validated_data)

        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Incorrect Credentials Passed.')
