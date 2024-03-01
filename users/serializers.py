from rest_framework import serializers
from .models import User

class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, required = True, style = {'input_type': 'password'})
    password_confirmation = serializers.CharField(write_only = True, required = True, style = {'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirmation', 'email', 'phone_number']

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirmation', None)
        return User.objects.create(username = validated_data['username'], password = validated_data['password'], email = validated_data['email'], phone_number = validated_data['phone_number'])
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'