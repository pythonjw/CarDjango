from rest_framework import serializers
from .models import UserInfo,CarInfo,UseCar


class CarInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model=CarInfo
        fields="__all__"



class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserInfo
        fields=('id','username','user_type','name')




class UseCarSerializer(serializers.ModelSerializer):
    carinfo=CarInfoSerializer()
    siji_userinfo=UserInfoSerializer()
    shenqingren_userinfo = UserInfoSerializer()
    class Meta:
        model=UseCar
        fields="__all__"




class UseCarNormal(serializers.ModelSerializer):
    carinfo = CarInfoSerializer()
    siji_userinfo = UserInfoSerializer()

    class Meta:
        model = UseCar
        fields = "__all__"


class UseCarForDriverSerializer(serializers.ModelSerializer):
    carinfo = CarInfoSerializer()
    shenqingren_userinfo = UserInfoSerializer()

    class Meta:
        model = UseCar
        fields = "__all__"





class UseCarAdd(serializers.ModelSerializer):
    class Meta:
        model=UseCar
        fields="__all__"