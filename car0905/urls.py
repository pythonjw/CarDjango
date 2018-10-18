"""car0905 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

from car.views import UserInfoViewSet, CarInfoViewSet, UseCarViewSet, UseCarViewSetAdd, UseCarViewSetNormal, \
    UseCarForDriver

router = DefaultRouter()
router.register(r'userinfo', UserInfoViewSet)
router.register(r'carinfo', CarInfoViewSet)
router.register(r'usecar', UseCarViewSet)
router.register(r'usecaradd', UseCarViewSetAdd)
router.register(r'usecarnormal', UseCarViewSetNormal)
router.register(r'usecarfordriver', UseCarForDriver)

from car import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', obtain_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),
    url(r'^', include(router.urls)),
    url('docs/', include_docs_urls(title='drf_docs')),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^qiniutoken$', views.QiniuToken.as_view()),
    url(r'^addmember$', views.AddMember.as_view()),
    url(r'^changepassword$', views.ChangePassword.as_view()),
    url(r'^queryusecartime$', views.QueryUseCarTime.as_view()),
    url(r'^querydriver$', views.QueryDriver.as_view()),
    url(r'^queryalldriverandcar$', views.QueryAllDriverAndCar.as_view()),
    url(r'^vehiclerecodedjango', views.VehicleRecodeDjango.as_view()),
url(r'^vehiclerecodeexcel', views.VehicleRecodeExcel.as_view()),
    url(r'^vehiclescheduledjango', views.VehicleScheduleDjango.as_view()),
    url(r'^emailhintdjango', views.EmailHintDjango.as_view()),
    url(r'^getexceldjango', views.GetExcelDjango.as_view()),
url(r'^agreeapply', views.AgreeApply.as_view()),
url(r'^disagreeapply', views.DisagreeApply.as_view()),
]
