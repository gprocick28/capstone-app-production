from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = User
        fields = ["id", "username", "password", "is_staff"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        is_staff = validated_data.pop("is_staff", False)
        
        validated_data["password"] = make_password(validated_data["password"])
        
        user = User.objects.create(**validated_data)

        if is_staff:
            user.is_staff = True
            user.save()

        return user


