# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-09-18 09:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0011_usecar'),
    ]

    operations = [
        migrations.AddField(
            model_name='usecar',
            name='beizhu',
            field=models.TextField(max_length=512, null=True),
        ),
    ]