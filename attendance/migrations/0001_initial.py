# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-18 00:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clubSetup', '0019_club_masterfile'),
    ]

    operations = [
        migrations.CreateModel(
            name='clubRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendance', models.IntegerField(default=0)),
                ('dues', models.FloatField(default=0)),
                ('stud', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubSetup.Student')),
            ],
        ),
    ]