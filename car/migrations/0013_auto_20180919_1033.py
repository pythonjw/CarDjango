# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-09-19 02:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0012_usecar_beizhu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usecar',
            name='using_time_start',
            field=models.DateTimeField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='usecar',
            name='using_time_stop',
            field=models.DateTimeField(db_index=True, null=True),
        ),
    ]