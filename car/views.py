from io import StringIO
import os,openpyxl

import view as view
from django.views import View
from car0905.settings import DEFAULT_FROM_EMAIL
from django.core.mail import send_mail
import time, json,datetime
import urllib.parse as upx

from xlwt import *

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from qiniu import Auth
from car.serializers import UserInfoSerializer, CarInfoSerializer, UseCarSerializer, UseCarAdd, UseCarNormal, \
    UseCarForDriverSerializer
from .models import UserInfo, CarInfo, UseCar
from django_filters.rest_framework import DjangoFilterBackend


# Create your views here.

class UserInfoViewSet(viewsets.ModelViewSet):
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('username',)


class CarInfoViewSet(viewsets.ModelViewSet):
    queryset = CarInfo.objects.all()
    serializer_class = CarInfoSerializer


class UseCarViewSet(viewsets.ModelViewSet):
    queryset = UseCar.objects.all()
    serializer_class = UseCarSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('status_code',)


class UseCarViewSetAdd(viewsets.ModelViewSet):
    queryset = UseCar.objects.all()
    serializer_class = UseCarAdd


class PaginationForUseCarViewSetNormal(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'p'


class UseCarViewSetNormal(viewsets.ModelViewSet):
    queryset = UseCar.objects.all()
    serializer_class = UseCarNormal
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('shenqingren_userinfo',)
    ordering_fields = ('application_date',)
    pagination_class = PaginationForUseCarViewSetNormal


class UseCarForDriver(viewsets.ModelViewSet):
    queryset = UseCar.objects.all()
    serializer_class = UseCarForDriverSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('siji_userinfo', 'status_code')


class QiniuToken(APIView):
    def get(self, request):
        access_key = '2QQVFuWnbMWjE400hMpxBRl3SQ5JytV6SdiSCvGw'
        secret_key = 'p1e79S0h8l2kPIiv1YM91VExh8acAIB3WiSlNyln'
        # 构建鉴权对象
        q = Auth(access_key, secret_key)
        # 要上传的空间
        bucket_name = 'jiongwen'
        # 上传到七牛后保存的文件名
        PictureName = request.META['QUERY_STRING'].split('=')[1]
        PictureName = str(time.time()).split('.')[0] + '_' + upx.unquote(
            request.META['QUERY_STRING'].split('=')[1].split('_')[0]) + '.' + PictureName.split('.')[1]
        key = 'PoscoIctChina' + '_' + PictureName
        # 上传策略示例
        # https://developer.qiniu.com/kodo/manual/1206/put-policy
        policy = {
            # 'callbackUrl':'https://requestb.in/1c7q2d31',
            # 'callbackBody':'filename=$(fname)&filesize=$(fsize)'
            # 'persistentOps':'imageView2/1/w/200/h/200'
            'mimeLimit': 'image/*',
        }
        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name, key, 3600, policy)
        # print(request.META.items())
        resp = {'token': token, 'key': key}
        print('key:' + key)
        print('token:' + token)
        return HttpResponse(json.dumps(resp), content_type="application/json")


class AddMember(APIView):
    def get(self, request):
        username = request.META['QUERY_STRING'].split('=')[1].split('_')[0]
        mname = upx.unquote(request.META['QUERY_STRING'].split('=')[1].split('_')[1])
        email = request.META['QUERY_STRING'].split('=')[1].split('_')[2]
        user_type = request.META['QUERY_STRING'].split('=')[1].split('_')[3]


        UserInfo.objects.create_user(username=username, password=username, user_type=user_type,receive_email=email,name=mname)
        return HttpResponse('ok')


class ChangePassword(APIView):
    def get(self, request):
        username = request.META['QUERY_STRING'].split('=')[1].split('_')[0]
        NewPassword = request.META['QUERY_STRING'].split('=')[1].split('_')[1]
        print(username)
        print(NewPassword)

        user_obj = UserInfo.objects.get(username__exact=username)
        user_obj.set_password(NewPassword)
        user_obj.save()
        return HttpResponse('ok')


class QueryUseCarTime(APIView):
    def get(self, request):
        RepeatList = []
        start_time = request.META['QUERY_STRING'].split('=')[1].split('_')[0].replace('+', ' ')
        stop_time = request.META['QUERY_STRING'].split('=')[1].split('_')[1].replace('+', ' ')
        start_time = int(time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M")))
        stop_time = int(time.mktime(time.strptime(stop_time, "%Y-%m-%d %H:%M")))

        db_time = UseCar.objects.filter(status_code__in=[2, 3])
        querySet = db_time.values('using_time_start', 'using_time_stop', 'carinfo_id', 'chufadi', 'mudidi', 'beizhu',
                                  'siji_userinfo__name', 'shenqingren_userinfo__name', 'carinfo__xinghao',
                                  'status_code')
        for i in querySet:
            s = str(i['using_time_start'])[0:19]
            t = str(i['using_time_stop'])[0:19]
            s = int(time.mktime(time.strptime(s, '%Y-%m-%d %X')))
            t = int(time.mktime(time.strptime(t, '%Y-%m-%d %X')))
            if stop_time - start_time == t - s:
                if stop_time > s and stop_time < t:
                    RepeatList.append({
                        'xinghao': i['carinfo__xinghao'],
                        'carinfo_id': i['carinfo_id'],
                        'siji': i['siji_userinfo__name'],
                        'shenqingren': i['shenqingren_userinfo__name'],
                        'chufadi': i['chufadi'],
                        'mudidi': i['mudidi'],
                        'beizhu': i['beizhu'],
                        'qishishijian': str(i['using_time_start'])[0:19],
                        'jieshushijian': str(i['using_time_stop'])[0:19],
                        'status_code': i['status_code'],
                    })
                elif stop_time == t:
                    RepeatList.append({
                        'xinghao': i['carinfo__xinghao'],
                        'carinfo_id': i['carinfo_id'],
                        'siji': i['siji_userinfo__name'],
                        'shenqingren': i['shenqingren_userinfo__name'],
                        'chufadi': i['chufadi'],
                        'mudidi': i['mudidi'],
                        'beizhu': i['beizhu'],
                        'qishishijian': str(i['using_time_start'])[0:19],
                        'jieshushijian': str(i['using_time_stop'])[0:19],
                        'status_code': i['status_code'],
                    })
                elif start_time > s and start_time < t:
                    RepeatList.append({
                        'xinghao': i['carinfo__xinghao'],
                        'carinfo_id': i['carinfo_id'],
                        'siji': i['siji_userinfo__name'],
                        'shenqingren': i['shenqingren_userinfo__name'],
                        'chufadi': i['chufadi'],
                        'mudidi': i['mudidi'],
                        'beizhu': i['beizhu'],
                        'qishishijian': str(i['using_time_start'])[0:19],
                        'jieshushijian': str(i['using_time_stop'])[0:19],
                        'status_code': i['status_code'],
                    })

            elif stop_time - start_time > t - s:
                if start_time == s:
                    RepeatList.append({
                        'xinghao': i['carinfo__xinghao'],
                        'carinfo_id': i['carinfo_id'],
                        'siji': i['siji_userinfo__name'],
                        'shenqingren': i['shenqingren_userinfo__name'],
                        'chufadi': i['chufadi'],
                        'mudidi': i['mudidi'],
                        'beizhu': i['beizhu'],
                        'qishishijian': str(i['using_time_start'])[0:19],
                        'jieshushijian': str(i['using_time_stop'])[0:19],
                        'status_code': i['status_code'],
                    })
                elif stop_time == t:
                    RepeatList.append({
                        'xinghao': i['carinfo__xinghao'],
                        'carinfo_id': i['carinfo_id'],
                        'siji': i['siji_userinfo__name'],
                        'shenqingren': i['shenqingren_userinfo__name'],
                        'chufadi': i['chufadi'],
                        'mudidi': i['mudidi'],
                        'beizhu': i['beizhu'],
                        'qishishijian': str(i['using_time_start'])[0:19],
                        'jieshushijian': str(i['using_time_stop'])[0:19],
                        'status_code': i['status_code'],
                    })
                elif s > start_time and s < stop_time:
                    RepeatList.append({
                        'xinghao': i['carinfo__xinghao'],
                        'carinfo_id': i['carinfo_id'],
                        'siji': i['siji_userinfo__name'],
                        'shenqingren': i['shenqingren_userinfo__name'],
                        'chufadi': i['chufadi'],
                        'mudidi': i['mudidi'],
                        'beizhu': i['beizhu'],
                        'qishishijian': str(i['using_time_start'])[0:19],
                        'jieshushijian': str(i['using_time_stop'])[0:19],
                        'status_code': i['status_code'],
                    })
                elif t > start_time and t < stop_time:
                    RepeatList.append({
                        'xinghao': i['carinfo__xinghao'],
                        'carinfo_id': i['carinfo_id'],
                        'siji': i['siji_userinfo__name'],
                        'shenqingren': i['shenqingren_userinfo__name'],
                        'chufadi': i['chufadi'],
                        'mudidi': i['mudidi'],
                        'beizhu': i['beizhu'],
                        'qishishijian': str(i['using_time_start'])[0:19],
                        'jieshushijian': str(i['using_time_stop'])[0:19],
                        'status_code': i['status_code'],
                    })

            elif stop_time - start_time < t - s:
                if start_time == s:
                    RepeatList.append({
                        'xinghao': i['carinfo__xinghao'],
                        'carinfo_id': i['carinfo_id'],
                        'siji': i['siji_userinfo__name'],
                        'shenqingren': i['shenqingren_userinfo__name'],
                        'chufadi': i['chufadi'],
                        'mudidi': i['mudidi'],
                        'beizhu': i['beizhu'],
                        'qishishijian': str(i['using_time_start'])[0:19],
                        'jieshushijian': str(i['using_time_stop'])[0:19],
                        'status_code': i['status_code'],
                    })
                elif stop_time == t:
                    RepeatList.append({
                        'xinghao': i['carinfo__xinghao'],
                        'carinfo_id': i['carinfo_id'],
                        'siji': i['siji_userinfo__name'],
                        'shenqingren': i['shenqingren_userinfo__name'],
                        'chufadi': i['chufadi'],
                        'mudidi': i['mudidi'],
                        'beizhu': i['beizhu'],
                        'qishishijian': str(i['using_time_start'])[0:19],
                        'jieshushijian': str(i['using_time_stop'])[0:19],
                        'status_code': i['status_code'],
                    })
                elif start_time > s and start_time < t:
                    RepeatList.append({
                        'xinghao': i['carinfo__xinghao'],
                        'carinfo_id': i['carinfo_id'],
                        'siji': i['siji_userinfo__name'],
                        'shenqingren': i['shenqingren_userinfo__name'],
                        'chufadi': i['chufadi'],
                        'mudidi': i['mudidi'],
                        'beizhu': i['beizhu'],
                        'qishishijian': str(i['using_time_start'])[0:19],
                        'jieshushijian': str(i['using_time_stop'])[0:19],
                        'status_code': i['status_code'],
                    })
                elif stop_time > s and stop_time < t:
                    RepeatList.append({
                        'xinghao': i['carinfo__xinghao'],
                        'carinfo_id': i['carinfo_id'],
                        'siji': i['siji_userinfo__name'],
                        'shenqingren': i['shenqingren_userinfo__name'],
                        'chufadi': i['chufadi'],
                        'mudidi': i['mudidi'],
                        'beizhu': i['beizhu'],
                        'qishishijian': str(i['using_time_start'])[0:19],
                        'jieshushijian': str(i['using_time_stop'])[0:19],

                        'status_code': i['status_code'],
                    })


        return HttpResponse(json.dumps(RepeatList), content_type="application/json")



class QueryDriver(APIView):
    def get(self, request):
        RepeatList = []
        start_time = request.META['QUERY_STRING'].split('=')[1].split('_')[0].replace('+', ' ')
        stop_time = request.META['QUERY_STRING'].split('=')[1].split('_')[1].replace('+', ' ')
        start_time = int(time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M")))
        stop_time = int(time.mktime(time.strptime(stop_time, "%Y-%m-%d %H:%M")))
        db_time = UseCar.objects.filter(status_code__in=[2, 3])
        querySet = db_time.values('using_time_start', 'using_time_stop', 'siji_userinfo__name', 'siji_userinfo')
        for i in querySet:
            s = str(i['using_time_start'])[0:19]
            t = str(i['using_time_stop'])[0:19]
            s = int(time.mktime(time.strptime(s, '%Y-%m-%d %X')))
            t = int(time.mktime(time.strptime(t, '%Y-%m-%d %X')))
            if stop_time - start_time == t - s:
                if stop_time > s and stop_time < t:
                    RepeatList.append({

                        'siji': i['siji_userinfo__name'],
                        'siji_id': i['siji_userinfo'],
                    })
                elif stop_time == t:
                    RepeatList.append({
                        'siji': i['siji_userinfo__name'],
                        'siji_id': i['siji_userinfo'],
                    })
                elif start_time > s and start_time < t:
                    RepeatList.append({
                        'siji': i['siji_userinfo__name'],
                        'siji_id': i['siji_userinfo'],
                    })

            elif stop_time - start_time > t - s:
                if start_time == s:
                    RepeatList.append({
                        'siji': i['siji_userinfo__name'],
                        'siji_id': i['siji_userinfo'],
                    })
                elif stop_time == t:
                    RepeatList.append({
                        'siji': i['siji_userinfo__name'],
                        'siji_id': i['siji_userinfo'],
                    })
                elif s > start_time and s < stop_time:
                    RepeatList.append({
                        'siji': i['siji_userinfo__name'],
                        'siji_id': i['siji_userinfo'],
                    })
                elif t > start_time and t < stop_time:
                    RepeatList.append({
                        'siji': i['siji_userinfo__name'],
                        'siji_id': i['siji_userinfo'],
                    })

            elif stop_time - start_time < t - s:
                if start_time == s:
                    RepeatList.append({
                        'siji': i['siji_userinfo__name'],
                        'siji_id': i['siji_userinfo'],
                    })
                elif stop_time == t:
                    RepeatList.append({
                        'siji': i['siji_userinfo__name'],
                        'siji_id': i['siji_userinfo'],
                    })
                elif start_time > s and start_time < t:
                    RepeatList.append({
                        'siji': i['siji_userinfo__name'],
                        'siji_id': i['siji_userinfo'],
                    })
                elif stop_time > s and stop_time < t:
                    RepeatList.append({
                        'siji': i['siji_userinfo__name'],
                        'siji_id': i['siji_userinfo'],
                    })
        driverObj = UserInfo.objects.exclude(user_type=3).order_by('username').values('id', 'username', 'name')
        RepeatList.append({'otherDrivers': list(driverObj)})
        allDriversObj = UserInfo.objects.filter(user_type=3).order_by('username').values('id', 'username', 'name')
        RepeatList.append({'allDrivers': list(allDriversObj)})
        print(RepeatList)
        return HttpResponse(json.dumps(RepeatList), content_type="application/json")


class QueryAllDriverAndCar(APIView):
    def get(self, request):
        AllDriverList = []
        AllCarList = []
        DriverObj = UserInfo.objects.exclude(user_type=3).order_by('username').values('id', 'username', 'name')
        for i in DriverObj:
            AllDriverList.append(i)
        CarObj = CarInfo.objects.all().values('id', 'xinghao')
        for i in CarObj:
            AllCarList.append(i)
        FinalList = [AllDriverList, AllCarList]
        return HttpResponse(json.dumps(FinalList), content_type="application/json")


class VehicleScheduleDjango(APIView):
    def get(self, request):
        def timecycle(year, mon, day):
            FormatTime = '%s-%s-%s' % (year, mon, day)
            shijianchuo = int(time.mktime(time.strptime(FormatTime, '%Y-%m-%d')))
            return shijianchuo
        ReturnDict={}
        beginDate=request.META['QUERY_STRING'].split(',')[0].split('=')[1]
        endDate=request.META['QUERY_STRING'].split(',')[1].split('__')[0]
        CarId=request.META['QUERY_STRING'].split('__')[1]
        dates = []
        print(beginDate)
        def dateRange(beginDate, endDate):
            dt = datetime.datetime.strptime(beginDate, '%Y-%m-%d')
            date = beginDate[:]
            while date <= endDate:
                dates.append(date)
                dt = dt + datetime.timedelta(1)
                date = dt.strftime('%Y-%m-%d')
            return dates
        dateRange(beginDate,endDate)

        ReturnDict['DateList']=dates
        ReturnDict['event'] = []


        UseCarObj = UseCar.objects.filter(status_code__in=[2, 3]).filter(carinfo=CarId).values('using_time_start','application_date',
   'status_code','siji_userinfo__name','shenqingren_userinfo__name','chufadi','mudidi','using_time_stop')
        start_time = int(time.mktime(time.strptime(beginDate, '%Y-%m-%d')))

        stop_time = int(time.mktime(time.strptime(endDate, '%Y-%m-%d'))) + 86400
        print(type(len(dates)))

        if  len(dates)==1:
            for i in UseCarObj:
                s = str(i['using_time_start'])[0:19]
                t = str(i['using_time_stop'])[0:19]

                s = int(time.mktime(time.strptime(s, '%Y-%m-%d %X')))
                t = int(time.mktime(time.strptime(t, '%Y-%m-%d %X')))
                # 我选单日X系统单日(code:1)
                if  start_time<s<t<stop_time:
                    linshiDICT=[]
                    linshiDICT.append('1')
                    linshiDICT.append(str(i['application_date'])[0:19])
                    linshiDICT.append(i['siji_userinfo__name'])
                    linshiDICT.append(str(i['using_time_start'])[0:19])
                    linshiDICT.append(str(i['using_time_stop'])[0:19])
                    linshiDICT.append(i['chufadi'])
                    linshiDICT.append(i['mudidi'])
                    linshiDICT.append(i['shenqingren_userinfo__name'])
                    if i['status_code']=='2':
                        linshiDICT.append('待决裁')
                    elif i['status_code']=='3':
                        linshiDICT.append('进行中')
                    ReturnDict['event'].append(linshiDICT)
                # 我选单日X系统多日(code:2)
                elif s<start_time<t<stop_time:
                    linshiDICT = []
                    linshiDICT.append('2')
                    linshiDICT.append(str(i['application_date'])[0:19])
                    linshiDICT.append(i['siji_userinfo__name'])
                    linshiDICT.append(str(i['using_time_start'])[0:19])
                    linshiDICT.append(str(i['using_time_stop'])[0:19])
                    linshiDICT.append(i['chufadi'])
                    linshiDICT.append(i['mudidi'])
                    linshiDICT.append(i['shenqingren_userinfo__name'])
                    if i['status_code'] == '2':
                        linshiDICT.append('待决裁')
                    elif i['status_code'] == '3':
                        linshiDICT.append('进行中')
                    ReturnDict['event'].append(linshiDICT)
                # 我选单日X系统多日(code:3)
                elif s<start_time<stop_time<t:
                    linshiDICT = []
                    linshiDICT.append('3')
                    linshiDICT.append(str(i['application_date'])[0:19])
                    linshiDICT.append(i['siji_userinfo__name'])
                    linshiDICT.append(str(i['using_time_start'])[0:19])
                    linshiDICT.append(str(i['using_time_stop'])[0:19])
                    linshiDICT.append(i['chufadi'])
                    linshiDICT.append(i['mudidi'])
                    linshiDICT.append(i['shenqingren_userinfo__name'])
                    if i['status_code'] == '2':
                        linshiDICT.append('待决裁')
                    elif i['status_code'] == '3':
                        linshiDICT.append('进行中')
                    ReturnDict['event'].append(linshiDICT)
                # 我选单日X系统多日(code:4)
                elif start_time<s<stop_time<t:
                    linshiDICT = []
                    linshiDICT.append('4')
                    linshiDICT.append(str(i['application_date'])[0:19])
                    linshiDICT.append(i['siji_userinfo__name'])
                    linshiDICT.append(str(i['using_time_start'])[0:19])
                    linshiDICT.append(str(i['using_time_stop'])[0:19])
                    linshiDICT.append(i['chufadi'])
                    linshiDICT.append(i['mudidi'])
                    linshiDICT.append(i['shenqingren_userinfo__name'])
                    if i['status_code'] == '2':
                        linshiDICT.append('待决裁')
                    elif i['status_code'] == '3':
                        linshiDICT.append('进行中')
                    ReturnDict['event'].append(linshiDICT)
        elif len(dates)>1:
            for i in UseCarObj:
                s = str(i['using_time_start'])[0:19]
                t = str(i['using_time_stop'])[0:19]
                shijianchuoS = int(time.mktime(time.strptime(s, '%Y-%m-%d %X')))
                shijianchuoT = int(time.mktime(time.strptime(t, '%Y-%m-%d %X')))
                ss=time.strptime(s, '%Y-%m-%d %X')
                tt = time.strptime(t, '%Y-%m-%d %X')
                bD = time.strptime(beginDate, '%Y-%m-%d')
                eD = time.strptime(endDate, '%Y-%m-%d')
                #数据库里的
                Syear=ss.tm_year
                Smon=ss.tm_mon
                Sday=ss.tm_mday
                Stime=timecycle(Syear,Smon,Sday)

                Tyear = tt.tm_year
                Tmon = tt.tm_mon
                Tday = tt.tm_mday
                Ttime=timecycle(Tyear,Tmon,Tday)
                #我自己选的
                Byear = bD.tm_year
                Bmon = bD.tm_mon
                Bday = bD.tm_mday
                Btime=timecycle(Byear,Bmon,Bday)

                Eyear = eD.tm_year
                Emon = eD.tm_mon
                Eday = eD.tm_mday
                Etime=timecycle(Eyear,Emon,Eday)
                # 我选多日X系统单日(code:5)
                if Syear==Tyear and Smon==Tmon and Sday==Tday:
                    if start_time<shijianchuoS<shijianchuoT<stop_time:
                        linshiDICT = []
                        linshiDICT.append('5')
                        linshiDICT.append(str(i['application_date'])[0:19])
                        linshiDICT.append(i['siji_userinfo__name'])
                        linshiDICT.append(str(i['using_time_start'])[0:19])
                        linshiDICT.append(str(i['using_time_stop'])[0:19])
                        linshiDICT.append(i['chufadi'])
                        linshiDICT.append(i['mudidi'])
                        linshiDICT.append(i['shenqingren_userinfo__name'])
                        if i['status_code'] == '2':
                            linshiDICT.append('待决裁')
                        elif i['status_code'] == '3':
                            linshiDICT.append('进行中')
                        ReturnDict['event'].append(linshiDICT)

                elif Syear!=Tyear or Smon!=Tmon or Sday!=Tday:

                    # 我选多日X系统多日(code:6)
                    if Syear==Byear and Smon==Bmon and Sday==Bday and Tyear==Eyear and Tmon==Emon and Tday==Eday:
                        linshiDICT = []
                        linshiDICT.append('6')
                        linshiDICT.append(str(i['application_date'])[0:19])
                        linshiDICT.append(i['siji_userinfo__name'])
                        linshiDICT.append(str(i['using_time_start'])[0:19])
                        linshiDICT.append(str(i['using_time_stop'])[0:19])
                        linshiDICT.append(i['chufadi'])
                        linshiDICT.append(i['mudidi'])
                        linshiDICT.append(i['shenqingren_userinfo__name'])
                        if i['status_code'] == '2':
                            linshiDICT.append('待决裁')
                        elif i['status_code'] == '3':
                            linshiDICT.append('进行中')
                        ReturnDict['event'].append(linshiDICT)

                    # 我选多日X系统多日(code:7)
                    elif Tyear == Byear and Tmon == Bmon and Tday == Bday :
                        linshiDICT = []
                        linshiDICT.append('7')
                        linshiDICT.append(str(i['application_date'])[0:19])
                        linshiDICT.append(i['siji_userinfo__name'])
                        linshiDICT.append(str(i['using_time_start'])[0:19])
                        linshiDICT.append(str(i['using_time_stop'])[0:19])
                        linshiDICT.append(i['chufadi'])
                        linshiDICT.append(i['mudidi'])
                        linshiDICT.append(i['shenqingren_userinfo__name'])
                        if i['status_code'] == '2':
                            linshiDICT.append('待决裁')
                        elif i['status_code'] == '3':
                            linshiDICT.append('进行中')
                        ReturnDict['event'].append(linshiDICT)
                    # 我选多日X系统多日(code:8)
                    elif Stime<Btime<Ttime<Etime:
                        linshiDICT = []
                        linshiDICT.append('8')
                        linshiDICT.append(str(i['application_date'])[0:19])
                        linshiDICT.append(i['siji_userinfo__name'])
                        linshiDICT.append(str(i['using_time_start'])[0:19])
                        linshiDICT.append(str(i['using_time_stop'])[0:19])
                        linshiDICT.append(i['chufadi'])
                        linshiDICT.append(i['mudidi'])
                        linshiDICT.append(i['shenqingren_userinfo__name'])
                        if i['status_code'] == '2':
                            linshiDICT.append('待决裁')
                        elif i['status_code'] == '3':
                            linshiDICT.append('进行中')
                        ReturnDict['event'].append(linshiDICT)
                    # 我选多日X系统多日(code:9)
                    elif Stime==Btime and Btime<Ttime<Etime:
                        linshiDICT = []
                        linshiDICT.append('9')
                        linshiDICT.append(str(i['application_date'])[0:19])
                        linshiDICT.append(i['siji_userinfo__name'])
                        linshiDICT.append(str(i['using_time_start'])[0:19])
                        linshiDICT.append(str(i['using_time_stop'])[0:19])
                        linshiDICT.append(i['chufadi'])
                        linshiDICT.append(i['mudidi'])
                        linshiDICT.append(i['shenqingren_userinfo__name'])
                        if i['status_code'] == '2':
                            linshiDICT.append('待决裁')
                        elif i['status_code'] == '3':
                            linshiDICT.append('进行中')
                        ReturnDict['event'].append(linshiDICT)
                    # 我选多日X系统多日(code:10)
                    elif Btime<Stime<Ttime<Etime:
                        linshiDICT = []
                        linshiDICT.append('10')
                        linshiDICT.append(str(i['application_date'])[0:19])
                        linshiDICT.append(i['siji_userinfo__name'])
                        linshiDICT.append(str(i['using_time_start'])[0:19])
                        linshiDICT.append(str(i['using_time_stop'])[0:19])
                        linshiDICT.append(i['chufadi'])
                        linshiDICT.append(i['mudidi'])
                        linshiDICT.append(i['shenqingren_userinfo__name'])
                        if i['status_code'] == '2':
                            linshiDICT.append('待决裁')
                        elif i['status_code'] == '3':
                            linshiDICT.append('进行中')
                        ReturnDict['event'].append(linshiDICT)
                    # 我选多日X系统多日(code:11)
                    elif Btime<Stime<Etime and Etime==Ttime:
                        linshiDICT = []
                        linshiDICT.append('11')
                        linshiDICT.append(str(i['application_date'])[0:19])
                        linshiDICT.append(i['siji_userinfo__name'])
                        linshiDICT.append(str(i['using_time_start'])[0:19])
                        linshiDICT.append(str(i['using_time_stop'])[0:19])
                        linshiDICT.append(i['chufadi'])
                        linshiDICT.append(i['mudidi'])
                        linshiDICT.append(i['shenqingren_userinfo__name'])
                        if i['status_code'] == '2':
                            linshiDICT.append('待决裁')
                        elif i['status_code'] == '3':
                            linshiDICT.append('进行中')
                        ReturnDict['event'].append(linshiDICT)
                    # 我选多日X系统多日(code:12)
                    elif Btime<Stime<Etime<Ttime:
                        linshiDICT = []
                        linshiDICT.append('12')
                        linshiDICT.append(str(i['application_date'])[0:19])
                        linshiDICT.append(i['siji_userinfo__name'])
                        linshiDICT.append(str(i['using_time_start'])[0:19])
                        linshiDICT.append(str(i['using_time_stop'])[0:19])
                        linshiDICT.append(i['chufadi'])
                        linshiDICT.append(i['mudidi'])
                        linshiDICT.append(i['shenqingren_userinfo__name'])
                        if i['status_code'] == '2':
                            linshiDICT.append('待决裁')
                        elif i['status_code'] == '3':
                            linshiDICT.append('进行中')
                        ReturnDict['event'].append(linshiDICT)
                    # 我选多日X系统多日(code:13)
                    elif Etime==Stime:
                        linshiDICT = []
                        linshiDICT.append('13')
                        linshiDICT.append(str(i['application_date'])[0:19])
                        linshiDICT.append(i['siji_userinfo__name'])
                        linshiDICT.append(str(i['using_time_start'])[0:19])
                        linshiDICT.append(str(i['using_time_stop'])[0:19])
                        linshiDICT.append(i['chufadi'])
                        linshiDICT.append(i['mudidi'])
                        linshiDICT.append(i['shenqingren_userinfo__name'])
                        if i['status_code'] == '2':
                            linshiDICT.append('待决裁')
                        elif i['status_code'] == '3':
                            linshiDICT.append('进行中')
                        ReturnDict['event'].append(linshiDICT)
                    # 我选多日X系统多日(code:14)
                    elif Stime<Btime<Ttime and Etime==Ttime:
                        linshiDICT = []
                        linshiDICT.append('14')
                        linshiDICT.append(str(i['application_date'])[0:19])
                        linshiDICT.append(i['siji_userinfo__name'])
                        linshiDICT.append(str(i['using_time_start'])[0:19])
                        linshiDICT.append(str(i['using_time_stop'])[0:19])
                        linshiDICT.append(i['chufadi'])
                        linshiDICT.append(i['mudidi'])
                        linshiDICT.append(i['shenqingren_userinfo__name'])
                        if i['status_code'] == '2':
                            linshiDICT.append('待决裁')
                        elif i['status_code'] == '3':
                            linshiDICT.append('进行中')
                        ReturnDict['event'].append(linshiDICT)
                    # 我选多日X系统多日(code:15)
                    elif Stime<Btime<Etime<Ttime:
                        linshiDICT = []
                        linshiDICT.append('15')
                        linshiDICT.append(str(i['application_date'])[0:19])
                        linshiDICT.append(i['siji_userinfo__name'])
                        linshiDICT.append(str(i['using_time_start'])[0:19])
                        linshiDICT.append(str(i['using_time_stop'])[0:19])
                        linshiDICT.append(i['chufadi'])
                        linshiDICT.append(i['mudidi'])
                        linshiDICT.append(i['shenqingren_userinfo__name'])
                        if i['status_code'] == '2':
                            linshiDICT.append('待决裁')
                        elif i['status_code'] == '3':
                            linshiDICT.append('进行中')
                        ReturnDict['event'].append(linshiDICT)
                    # 我选多日X系统多日(code:16)
                    elif Btime==Stime and Stime<Etime<Ttime:
                        linshiDICT = []
                        linshiDICT.append('16')
                        linshiDICT.append(str(i['application_date'])[0:19])
                        linshiDICT.append(i['siji_userinfo__name'])
                        linshiDICT.append(str(i['using_time_start'])[0:19])
                        linshiDICT.append(str(i['using_time_stop'])[0:19])
                        linshiDICT.append(i['chufadi'])
                        linshiDICT.append(i['mudidi'])
                        linshiDICT.append(i['shenqingren_userinfo__name'])
                        if i['status_code'] == '2':
                            linshiDICT.append('待决裁')
                        elif i['status_code'] == '3':
                            linshiDICT.append('进行中')
                        ReturnDict['event'].append(linshiDICT)





        ReturnDict['beginDate']=beginDate
        ReturnDict['endDate']=endDate
        return HttpResponse(json.dumps(ReturnDict), content_type="application/json")

       #return HttpResponse('ok')


class EmailHintDjango(APIView):
    def get(self,request):
        email_title = "XXX1"
        email_body = "XXX1"
        email_to = "744684245@qq.com"
        send_status = send_mail(email_title, email_body, DEFAULT_FROM_EMAIL, [email_to])
        email_title = "XXX2"
        email_body = "XXX2"
        email_to = "744684245@qq.com"
        send_status = send_mail(email_title, email_body, DEFAULT_FROM_EMAIL, [email_to])

        return HttpResponse('ok')

class AgreeApply(APIView):
    def get(self,request):
        UseCarId=request.META['QUERY_STRING'].split('=')[1]
        obj=UseCar.objects.filter(id=UseCarId)
        obj.update(status_code=3)
        Fobj=obj.values('shenqingren_userinfo__receive_email','carinfo__xinghao','shenqingren_userinfo__name','siji_userinfo__receive_email','application_date','using_time_start','using_time_stop','chufadi','mudidi')
        ShenqingrenEmailAddress=Fobj[0][
            'shenqingren_userinfo__receive_email']
        SijiEmailAddress = Fobj[0][
            'siji_userinfo__receive_email']
        application_date=str(Fobj[0]['application_date'])[0:16]
        using_time_start=str(Fobj[0]['using_time_start'])[0:16]
        using_time_stop=str(Fobj[0]['using_time_stop'])[0:16]
        chufadi=Fobj[0]['chufadi']
        mudidi=Fobj[0]['mudidi']
        ShenqingrenName=Fobj[0][
            'shenqingren_userinfo__name']
        car=Fobj[0]['carinfo__xinghao']

        email_title = "恭喜您，申请车辆成功！"
        email_body = "您 "+application_date+' 申请的 '+car+' '+chufadi+' 至 '+mudidi+' , '+using_time_start+' 到 '+using_time_stop+' 的用车申请已通过审核！'
        email_to = ShenqingrenEmailAddress
        send_status = send_mail(email_title, email_body, DEFAULT_FROM_EMAIL, [email_to])
        email_title = "您有新的任务！"
        email_body =ShenqingrenName+ " "+application_date+' 申请的 '+car+' '+chufadi+' 至 '+mudidi+' , '+using_time_start+' 到 '+using_time_stop+' 的用车申请已通过审核！'
        email_to = SijiEmailAddress
        send_status = send_mail(email_title, email_body, DEFAULT_FROM_EMAIL, [email_to])
        return HttpResponse('ok')

class DisagreeApply(APIView):
    def get(self,request):
        UseCarId=request.META['QUERY_STRING'].split('=')[1]
        obj=UseCar.objects.filter(id=UseCarId)
        obj.update(status_code=4)
        Fobj=obj.values('shenqingren_userinfo__receive_email','carinfo__xinghao','application_date','using_time_start','using_time_stop','chufadi','mudidi')
        ShenqingrenEmailAddress=Fobj[0][
            'shenqingren_userinfo__receive_email']

        application_date=str(Fobj[0]['application_date'])[0:16]
        using_time_start=str(Fobj[0]['using_time_start'])[0:16]
        using_time_stop=str(Fobj[0]['using_time_stop'])[0:16]
        chufadi=Fobj[0]['chufadi']
        mudidi=Fobj[0]['mudidi']

        car=Fobj[0]['carinfo__xinghao']

        email_title = "很遗憾，您的车辆申请未通过。"
        email_body = "您 "+application_date+' 申请的 '+car+' '+chufadi+' 至 '+mudidi+' , '+using_time_start+' 到 '+using_time_stop+' 的用车申请未通过。'
        email_to = ShenqingrenEmailAddress
        send_status = send_mail(email_title, email_body, DEFAULT_FROM_EMAIL, [email_to])
        return HttpResponse('ok')



class GetExcelDjango(APIView):
    def get(self,requset):
        """
            导出excel表格
            """
        list_obj = UseCar.objects.filter('id')
        if list_obj:
            # 创建工作薄
            ws = Workbook(encoding='utf-8')
            w = ws.add_sheet(u"数据报表第一页")
            w.write(0, 0, "id")
            # w.write(0, 1, u"用户名")
            # w.write(0, 2, u"发布时间")
            # w.write(0, 3, u"内容")
            # w.write(0, 4, u"来源")
            # 写入数据
            excel_row = 1
            for obj in list_obj:
                data_id = obj.id
                # data_user = obj.username
                # data_time = obj.time.strftime("%Y-%m-%d")[:10]
                # data_content = obj.content
                # dada_source = obj.source
                w.write(excel_row, 0, data_id)
                # w.write(excel_row, 1, data_user)
                # w.write(excel_row, 2, data_time)
                # w.write(excel_row, 3, data_content)
                # w.write(excel_row, 4, dada_source)
                excel_row += 1
            # 检测文件是够存在
            # 方框中代码是保存本地文件使用，如不需要请删除该代码
            ###########################
            exist_file = os.path.exists("test.xls")
            if exist_file:
                os.remove(r"test.xls")
            ws.save("test.xls")
            ############################
            sio = StringIO()
            ws.save(sio)
            sio.seek(0)
            response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=test.xls'
            response.write(sio.getvalue())
            return response


class VehicleRecodeDjango(APIView):
    def get(self, request):
        ReturnList = []
        CarId = request.META['QUERY_STRING'].split('__')[-1]
        UserName = request.META['QUERY_STRING'].split('__')[-2]
        using_time_start = ''
        using_time_stop = ''
        TimeFlag = request.META['QUERY_STRING'].split('__')[0].split('=')[1]
        if TimeFlag == 'all':
            using_time_start = TimeFlag
            using_time_stop = TimeFlag
        elif TimeFlag != 'all':
            using_time_start = TimeFlag.split('_')[0].split('+')[0] + ' ' + TimeFlag.split('_')[0].split('+')[1]
            using_time_stop = TimeFlag.split('_')[1].split('+')[0] + ' ' + TimeFlag.split('_')[1].split('+')[1]

        if CarId == 'all':
            RecodeObj = UseCar.objects
            if UserName == 'all':
                RecodeObj = RecodeObj
                if using_time_start == 'all':
                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')
                    for i in RecodeObj:
                        ReturnList.append({
                            'ShenQingShiJian': str(i['application_date'])[0:19],
                            'XingHao': i['carinfo__xinghao'],
                            'ShenQingRen': i['shenqingren_userinfo__name'],
                            'QiShiShiJian': str(i['using_time_start'])[0:19],
                            'JieShuShiJian': str(i['using_time_stop'])[0:19],
                            'ChuFaDi': i['chufadi'],
                            'MuDiDi': i['mudidi'],
                            'StatusCode': i['status_code'],
                            'SiJi': i['siji_userinfo__name'],
                            'BeiZhu': i['beizhu'],
                        })
                elif using_time_start != 'all':

                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')
                    for i in RecodeObj:
                        using_time_start_timestamp = time.mktime(time.strptime(using_time_start, '%Y-%m-%d %X'))
                        using_time_stop_timestamp = time.mktime(time.strptime(using_time_stop, '%Y-%m-%d %X'))
                        application_date_timestamp = time.mktime(
                            time.strptime(str(i['application_date'])[0:19], '%Y-%m-%d %X'))
                        if using_time_start_timestamp <= application_date_timestamp and application_date_timestamp <= using_time_stop_timestamp:
                            ReturnList.append({
                                'ShenQingShiJian': str(i['application_date'])[0:19],
                                'XingHao': i['carinfo__xinghao'],
                                'ShenQingRen': i['shenqingren_userinfo__name'],
                                'QiShiShiJian': str(i['using_time_start'])[0:19],
                                'JieShuShiJian': str(i['using_time_stop'])[0:19],
                                'ChuFaDi': i['chufadi'],
                                'MuDiDi': i['mudidi'],
                                'StatusCode': i['status_code'],
                                'SiJi': i['siji_userinfo__name'],
                                'BeiZhu': i['beizhu'],
                            })


            elif UserName != 'all':
                RecodeObj = RecodeObj.filter(shenqingren_userinfo__username=UserName)
                if using_time_start == 'all':

                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')

                    for i in RecodeObj:
                        ReturnList.append({
                            'ShenQingShiJian': str(i['application_date'])[0:19],
                            'XingHao': i['carinfo__xinghao'],
                            'ShenQingRen': i['shenqingren_userinfo__name'],
                            'QiShiShiJian': str(i['using_time_start'])[0:19],
                            'JieShuShiJian': str(i['using_time_stop'])[0:19],
                            'ChuFaDi': i['chufadi'],
                            'MuDiDi': i['mudidi'],
                            'StatusCode': i['status_code'],
                            'SiJi': i['siji_userinfo__name'],
                            'BeiZhu': i['beizhu'],
                        })
                elif using_time_start != 'all':
                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')
                    for i in RecodeObj:
                        using_time_start_timestamp = time.mktime(time.strptime(using_time_start, '%Y-%m-%d %X'))
                        using_time_stop_timestamp = time.mktime(time.strptime(using_time_stop, '%Y-%m-%d %X'))
                        application_date_timestamp = time.mktime(
                            time.strptime(str(i['application_date'])[0:19], '%Y-%m-%d %X'))
                        if using_time_start_timestamp <= application_date_timestamp and application_date_timestamp <= using_time_stop_timestamp:
                            ReturnList.append({
                                'ShenQingShiJian': str(i['application_date'])[0:19],
                                'XingHao': i['carinfo__xinghao'],
                                'ShenQingRen': i['shenqingren_userinfo__name'],
                                'QiShiShiJian': str(i['using_time_start'])[0:19],
                                'JieShuShiJian': str(i['using_time_stop'])[0:19],
                                'ChuFaDi': i['chufadi'],
                                'MuDiDi': i['mudidi'],
                                'StatusCode': i['status_code'],
                                'SiJi': i['siji_userinfo__name'],
                                'BeiZhu': i['beizhu'],
                            })
        elif CarId != 'all':
            RecodeObj = UseCar.objects.filter(carinfo=CarId)
            if UserName == 'all':
                RecodeObj = RecodeObj
                if using_time_start == 'all':
                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')

                    for i in RecodeObj:
                        ReturnList.append({
                            'ShenQingShiJian': str(i['application_date'])[0:19],
                            'XingHao': i['carinfo__xinghao'],
                            'ShenQingRen': i['shenqingren_userinfo__name'],
                            'QiShiShiJian': str(i['using_time_start'])[0:19],
                            'JieShuShiJian': str(i['using_time_stop'])[0:19],
                            'ChuFaDi': i['chufadi'],
                            'MuDiDi': i['mudidi'],
                            'StatusCode': i['status_code'],
                            'SiJi': i['siji_userinfo__name'],
                            'BeiZhu': i['beizhu'],
                        })
                elif using_time_start != 'all':
                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')
                    for i in RecodeObj:
                        using_time_start_timestamp = time.mktime(time.strptime(using_time_start, '%Y-%m-%d %X'))
                        using_time_stop_timestamp = time.mktime(time.strptime(using_time_stop, '%Y-%m-%d %X'))
                        application_date_timestamp = time.mktime(
                            time.strptime(str(i['application_date'])[0:19], '%Y-%m-%d %X'))
                        if using_time_start_timestamp <= application_date_timestamp and application_date_timestamp <= using_time_stop_timestamp:
                            ReturnList.append({
                                'ShenQingShiJian': str(i['application_date'])[0:19],
                                'XingHao': i['carinfo__xinghao'],
                                'ShenQingRen': i['shenqingren_userinfo__name'],
                                'QiShiShiJian': str(i['using_time_start'])[0:19],
                                'JieShuShiJian': str(i['using_time_stop'])[0:19],
                                'ChuFaDi': i['chufadi'],
                                'MuDiDi': i['mudidi'],
                                'StatusCode': i['status_code'],
                                'SiJi': i['siji_userinfo__name'],
                                'BeiZhu': i['beizhu'],
                            })
            elif UserName != 'all':
                RecodeObj = RecodeObj.filter(shenqingren_userinfo__username=UserName)
                if using_time_start == 'all':
                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')

                    for i in RecodeObj:
                        ReturnList.append({
                            'ShenQingShiJian': str(i['application_date'])[0:19],
                            'XingHao': i['carinfo__xinghao'],
                            'ShenQingRen': i['shenqingren_userinfo__name'],
                            'QiShiShiJian': str(i['using_time_start'])[0:19],
                            'JieShuShiJian': str(i['using_time_stop'])[0:19],
                            'ChuFaDi': i['chufadi'],
                            'MuDiDi': i['mudidi'],
                            'StatusCode': i['status_code'],
                            'SiJi': i['siji_userinfo__name'],
                            'BeiZhu': i['beizhu'],
                        })
                elif using_time_start != 'all':
                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')
                    for i in RecodeObj:
                        using_time_start_timestamp = time.mktime(time.strptime(using_time_start, '%Y-%m-%d %X'))
                        using_time_stop_timestamp = time.mktime(time.strptime(using_time_stop, '%Y-%m-%d %X'))
                        application_date_timestamp = time.mktime(
                            time.strptime(str(i['application_date'])[0:19], '%Y-%m-%d %X'))
                        if using_time_start_timestamp <= application_date_timestamp and application_date_timestamp <= using_time_stop_timestamp:
                            ReturnList.append({
                                'ShenQingShiJian': str(i['application_date'])[0:19],
                                'XingHao': i['carinfo__xinghao'],
                                'ShenQingRen': i['shenqingren_userinfo__name'],
                                'QiShiShiJian': str(i['using_time_start'])[0:19],
                                'JieShuShiJian': str(i['using_time_stop'])[0:19],
                                'ChuFaDi': i['chufadi'],
                                'MuDiDi': i['mudidi'],
                                'StatusCode': i['status_code'],
                                'SiJi': i['siji_userinfo__name'],
                                'BeiZhu': i['beizhu'],
                            })
        print(ReturnList)
        return HttpResponse(json.dumps(ReturnList), content_type="application/json")

class VehicleRecodeExcel(APIView):
    def get(self, request):
        NowTime=int(time.time())
        NowTimeFlag=NowTime-3600
        FileList=[]
        for root, dirs, files in os.walk('C:\PycharmProjects\car0905\statics\excel'):
            print('123')
            FileList=files

        for i in FileList:
            Fname=i.split('.')[0]
            if int(Fname)<NowTimeFlag:
                os.remove('C:\PycharmProjects\car0905\statics\excel\\'+i)
        ReturnList = []
        CarId = request.META['QUERY_STRING'].split('__')[-1]
        UserName = request.META['QUERY_STRING'].split('__')[-2]
        using_time_start = ''
        using_time_stop = ''
        TimeFlag = request.META['QUERY_STRING'].split('__')[0].split('=')[1]
        if TimeFlag == 'all':
            using_time_start = TimeFlag
            using_time_stop = TimeFlag
        elif TimeFlag != 'all':
            using_time_start = TimeFlag.split('_')[0].split('+')[0] + ' ' + TimeFlag.split('_')[0].split('+')[1]
            using_time_stop = TimeFlag.split('_')[1].split('+')[0] + ' ' + TimeFlag.split('_')[1].split('+')[1]

        if CarId == 'all':
            RecodeObj = UseCar.objects
            if UserName == 'all':
                RecodeObj = RecodeObj
                if using_time_start == 'all':
                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')
                    for i in RecodeObj:
                        ReturnList.append({
                            'ShenQingShiJian': str(i['application_date'])[0:19],
                            'XingHao': i['carinfo__xinghao'],
                            'ShenQingRen': i['shenqingren_userinfo__name'],
                            'QiShiShiJian': str(i['using_time_start'])[0:19],
                            'JieShuShiJian': str(i['using_time_stop'])[0:19],
                            'ChuFaDi': i['chufadi'],
                            'MuDiDi': i['mudidi'],
                            'StatusCode': i['status_code'],
                            'SiJi': i['siji_userinfo__name'],
                            'BeiZhu': i['beizhu'],
                        })
                elif using_time_start != 'all':

                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')
                    for i in RecodeObj:
                        using_time_start_timestamp = time.mktime(time.strptime(using_time_start, '%Y-%m-%d %X'))
                        using_time_stop_timestamp = time.mktime(time.strptime(using_time_stop, '%Y-%m-%d %X'))
                        application_date_timestamp = time.mktime(
                            time.strptime(str(i['application_date'])[0:19], '%Y-%m-%d %X'))
                        if using_time_start_timestamp <= application_date_timestamp and application_date_timestamp <= using_time_stop_timestamp:
                            ReturnList.append({
                                'ShenQingShiJian': str(i['application_date'])[0:19],
                                'XingHao': i['carinfo__xinghao'],
                                'ShenQingRen': i['shenqingren_userinfo__name'],
                                'QiShiShiJian': str(i['using_time_start'])[0:19],
                                'JieShuShiJian': str(i['using_time_stop'])[0:19],
                                'ChuFaDi': i['chufadi'],
                                'MuDiDi': i['mudidi'],
                                'StatusCode': i['status_code'],
                                'SiJi': i['siji_userinfo__name'],
                                'BeiZhu': i['beizhu'],
                            })


            elif UserName != 'all':
                RecodeObj = RecodeObj.filter(shenqingren_userinfo__username=UserName)
                if using_time_start == 'all':

                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')

                    for i in RecodeObj:
                        ReturnList.append({
                            'ShenQingShiJian': str(i['application_date'])[0:19],
                            'XingHao': i['carinfo__xinghao'],
                            'ShenQingRen': i['shenqingren_userinfo__name'],
                            'QiShiShiJian': str(i['using_time_start'])[0:19],
                            'JieShuShiJian': str(i['using_time_stop'])[0:19],
                            'ChuFaDi': i['chufadi'],
                            'MuDiDi': i['mudidi'],
                            'StatusCode': i['status_code'],
                            'SiJi': i['siji_userinfo__name'],
                            'BeiZhu': i['beizhu'],
                        })
                elif using_time_start != 'all':
                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')
                    for i in RecodeObj:
                        using_time_start_timestamp = time.mktime(time.strptime(using_time_start, '%Y-%m-%d %X'))
                        using_time_stop_timestamp = time.mktime(time.strptime(using_time_stop, '%Y-%m-%d %X'))
                        application_date_timestamp = time.mktime(
                            time.strptime(str(i['application_date'])[0:19], '%Y-%m-%d %X'))
                        if using_time_start_timestamp <= application_date_timestamp and application_date_timestamp <= using_time_stop_timestamp:
                            ReturnList.append({
                                'ShenQingShiJian': str(i['application_date'])[0:19],
                                'XingHao': i['carinfo__xinghao'],
                                'ShenQingRen': i['shenqingren_userinfo__name'],
                                'QiShiShiJian': str(i['using_time_start'])[0:19],
                                'JieShuShiJian': str(i['using_time_stop'])[0:19],
                                'ChuFaDi': i['chufadi'],
                                'MuDiDi': i['mudidi'],
                                'StatusCode': i['status_code'],
                                'SiJi': i['siji_userinfo__name'],
                                'BeiZhu': i['beizhu'],
                            })
        elif CarId != 'all':
            RecodeObj = UseCar.objects.filter(carinfo=CarId)
            if UserName == 'all':
                RecodeObj = RecodeObj
                if using_time_start == 'all':
                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')

                    for i in RecodeObj:
                        ReturnList.append({
                            'ShenQingShiJian': str(i['application_date'])[0:19],
                            'XingHao': i['carinfo__xinghao'],
                            'ShenQingRen': i['shenqingren_userinfo__name'],
                            'QiShiShiJian': str(i['using_time_start'])[0:19],
                            'JieShuShiJian': str(i['using_time_stop'])[0:19],
                            'ChuFaDi': i['chufadi'],
                            'MuDiDi': i['mudidi'],
                            'StatusCode': i['status_code'],
                            'SiJi': i['siji_userinfo__name'],
                            'BeiZhu': i['beizhu'],
                        })
                elif using_time_start != 'all':
                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')
                    for i in RecodeObj:
                        using_time_start_timestamp = time.mktime(time.strptime(using_time_start, '%Y-%m-%d %X'))
                        using_time_stop_timestamp = time.mktime(time.strptime(using_time_stop, '%Y-%m-%d %X'))
                        application_date_timestamp = time.mktime(
                            time.strptime(str(i['application_date'])[0:19], '%Y-%m-%d %X'))
                        if using_time_start_timestamp <= application_date_timestamp and application_date_timestamp <= using_time_stop_timestamp:
                            ReturnList.append({
                                'ShenQingShiJian': str(i['application_date'])[0:19],
                                'XingHao': i['carinfo__xinghao'],
                                'ShenQingRen': i['shenqingren_userinfo__name'],
                                'QiShiShiJian': str(i['using_time_start'])[0:19],
                                'JieShuShiJian': str(i['using_time_stop'])[0:19],
                                'ChuFaDi': i['chufadi'],
                                'MuDiDi': i['mudidi'],
                                'StatusCode': i['status_code'],
                                'SiJi': i['siji_userinfo__name'],
                                'BeiZhu': i['beizhu'],
                            })
            elif UserName != 'all':
                RecodeObj = RecodeObj.filter(shenqingren_userinfo__username=UserName)
                if using_time_start == 'all':
                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')

                    for i in RecodeObj:
                        ReturnList.append({
                            'ShenQingShiJian': str(i['application_date'])[0:19],
                            'XingHao': i['carinfo__xinghao'],
                            'ShenQingRen': i['shenqingren_userinfo__name'],
                            'QiShiShiJian': str(i['using_time_start'])[0:19],
                            'JieShuShiJian': str(i['using_time_stop'])[0:19],
                            'ChuFaDi': i['chufadi'],
                            'MuDiDi': i['mudidi'],
                            'StatusCode': i['status_code'],
                            'SiJi': i['siji_userinfo__name'],
                            'BeiZhu': i['beizhu'],
                        })
                elif using_time_start != 'all':
                    RecodeObj = RecodeObj.values('application_date', 'carinfo__xinghao',
                                                 'shenqingren_userinfo__name', 'using_time_start', 'using_time_stop',
                                                 'chufadi', 'mudidi', 'status_code', 'siji_userinfo__name', 'beizhu')
                    for i in RecodeObj:
                        using_time_start_timestamp = time.mktime(time.strptime(using_time_start, '%Y-%m-%d %X'))
                        using_time_stop_timestamp = time.mktime(time.strptime(using_time_stop, '%Y-%m-%d %X'))
                        application_date_timestamp = time.mktime(
                            time.strptime(str(i['application_date'])[0:19], '%Y-%m-%d %X'))
                        if using_time_start_timestamp <= application_date_timestamp and application_date_timestamp <= using_time_stop_timestamp:
                            ReturnList.append({
                                'ShenQingShiJian': str(i['application_date'])[0:19],
                                'XingHao': i['carinfo__xinghao'],
                                'ShenQingRen': i['shenqingren_userinfo__name'],
                                'QiShiShiJian': str(i['using_time_start'])[0:19],
                                'JieShuShiJian': str(i['using_time_stop'])[0:19],
                                'ChuFaDi': i['chufadi'],
                                'MuDiDi': i['mudidi'],
                                'StatusCode': i['status_code'],
                                'SiJi': i['siji_userinfo__name'],
                                'BeiZhu': i['beizhu'],
                            })

        wb = openpyxl.Workbook()  # 获取excel文件对象
        ws = wb.active  # 创建文件时默认的工作表对象
        ws.title = 'Car'  # 设置工作表名称

        ws['A1'] = '申请时间'  # 给特定的单元格赋值
        wb['Car'].column_dimensions['A'].width = 22
        ws['B1'] = '车辆型号'
        wb['Car'].column_dimensions['B'].width = 13
        ws['C1'] = '申请人'
        ws['D1'] = '始发地'
        wb['Car'].column_dimensions['D'].width = 13
        ws['E1'] = '目的地'
        wb['Car'].column_dimensions['E'].width = 13
        ws['F1'] = '状态'
        ws['G1'] = '起始时间'
        wb['Car'].column_dimensions['G'].width = 22
        ws['H1'] = '结束时间'
        wb['Car'].column_dimensions['H'].width = 22
        ws['I1'] = '司机'
        ws['J1'] = '备注'
        wb['Car'].column_dimensions['J'].width = 22
        for i in ReturnList:
            AppendList=[]
            AppendList.append(i.get('ShenQingShiJian'))
            AppendList.append(i.get('XingHao'))
            AppendList.append(i.get('ShenQingRen'))
            AppendList.append(i.get('ChuFaDi'))
            AppendList.append(i.get('MuDiDi'))
            StatusChinese=''
            if i.get('StatusCode')=='1':
                StatusChinese = '已完成'
            elif i.get('StatusCode')=='2':
                StatusChinese = '待审批'
            elif i.get('StatusCode')=='3':
                StatusChinese = '进行中'
            elif i.get('StatusCode')=='4':
                StatusChinese = '已拒绝'
            AppendList.append(StatusChinese)
            AppendList.append(i.get('QiShiShiJian'))
            AppendList.append(i.get('JieShuShiJian'))
            AppendList.append(i.get('SiJi'))
            AppendList.append(i.get('BeiZhu'))
            ws.append(AppendList)
        ExcelName=(str(NowTime))+'.xlsx'
        wb.save('C:\PycharmProjects\car0905\statics\excel\\'+ExcelName)
        #wb.save('iii.xlsx')
        return HttpResponse('http://127.0.0.1:8000/static/excel/'+ExcelName)