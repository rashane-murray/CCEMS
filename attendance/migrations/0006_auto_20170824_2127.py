# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-25 02:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0005_auto_20170823_2106'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clubrecord',
            old_name='criteria0',
            new_name='criteria3',
        ),
    ]