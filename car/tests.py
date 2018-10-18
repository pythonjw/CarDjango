import time
#code1,2返回格式
ReturnDict={
    'DateList':[],
    'code':'x',
    'event':[
        ['申请时间','状态','起始时间','结束时间','出发地','目的地','申请人','司机',],
        ['申请时间', '状态', '起始时间', '结束时间', '出发地', '目的地', '申请人', '司机', ],
    ],
}


a='2018-10-16'
b=time.mktime(time.strptime(a, '%Y-%m-%d'))


def timecycle(year,mon,day):
    FormatTime='%s-%s-%s'%(year,mon,day)
    shijianchuo=int(time.mktime(time.strptime(FormatTime, '%Y-%m-%d')))
    return shijianchuo

a=timecycle('2018','09','08')
print(a)
