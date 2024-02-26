
from rest_framework import serializers
from .models import User,Space,Post


# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        # fields = ['name', 'avatar', 'open_id','create_time']


# Serializers define the API representation.
class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = '__all__'
        # fields = ['name', 'owner', 'users','create_time']


class PostSerializerForGET(serializers.ModelSerializer):
    users = UserSerializer(many=True)
    class Meta:
        model = Post
        fields = '__all__'
        depth = 1


class PostSerializerForPOST(serializers.ModelSerializer):
    # users = UserSerializer(many=True)
    class Meta:
        model = Post
        fields = '__all__'
