from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = super().create(validated_data)
        user.set_password(make_password(password))
        user.save()
        return user


# class RegisterUserSeraializer(serializers.Serializer):
#     email = serializers.EmailField()
#     username = serializers.CharField()
#     password1 = serializers.CharField()
#     password2 = serializers.CharField()
#     first_name = serializers.CharField()
#     last_name = serializers.CharField()
#     date_of_birth = serializers.DateField()
#     gender = serializers.CharField()
