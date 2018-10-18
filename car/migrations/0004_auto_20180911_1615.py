# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-09-11 08:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0003_auto_20180911_1002'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepartmentInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(max_length=32)),
            ],
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='department',
        ),
    ]