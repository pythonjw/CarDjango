from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.




class UserInfo(AbstractUser):
    type_choices=((1,'普通用户'),(2,'管理用户'),(3,'司机'))
    user_type=models.IntegerField(choices=type_choices,default=1)
    name=models.CharField(max_length=32,default='名字')
    receive_email=models.CharField(max_length=47,default='xxx@xx.com')

class CarInfo(models.Model):
    renshu=models.CharField(max_length=32,null=True)
    chepai=models.CharField(max_length=32,null=True)
    xinghao=models.CharField(max_length=32,null=True)
    chejia=models.CharField(max_length=32,null=True)
    tupian=models.CharField(max_length=256,null=True)
    beizhu=models.TextField(max_length=512,null=True)
    PicHash = models.TextField(max_length=512, null=True)
    fuwu=models.CharField(max_length=1,null=True)

class UseCar(models.Model):
    application_date = models.DateTimeField(auto_now_add=True)
    #1是已完成，2是待审批，3是进行中，4是被拒绝
    status_code = models.CharField(max_length=1, default='2', db_index=True)

    # 1是还没看的，2是已看完的
    NormalUserTip = models.CharField(max_length=1, default='0',)

    RefuseReason= models.TextField(max_length=512, null=True)


    using_time_start = models.DateTimeField(db_index=True,null=True)
    using_time_stop = models.DateTimeField(db_index=True,null=True)
    carinfo = models.ForeignKey("CarInfo", null=True, on_delete=models.SET_NULL, related_name="f_OM_carinfo_usecar_rn",
                            related_query_name="f_OM_carinfo_usecar_rqn", )
    siji_userinfo = models.ForeignKey("UserInfo", null=True, on_delete=models.SET_NULL,
                                  related_name="siji_f_OM_userinfo_usecar_rn",
                                  related_query_name="siji_f_OM_userinfo_usecar_rqn")
    shenqingren_userinfo = models.ForeignKey("UserInfo", null=True, on_delete=models.SET_NULL,
                                         related_name="shenqingren_f_OM_userinfo_usecar_rn",
                                         related_query_name="shenqingren_f_OM_userinfo_usecar_rqn")
    # MM_employee=models.ManyToManyField("Employee",related_name="MM_employee_usecar_rn",related_query_name="MM_employee_usecar_rqn")
    chufadi = models.CharField(max_length=77, null=True)
    mudidi = models.CharField(max_length=77, null=True)
    beizhu = models.TextField(max_length=512, null=True)
    beforedistance= models.CharField(max_length=77, null=True)
    afterdistance= models.CharField(max_length=77, null=True)