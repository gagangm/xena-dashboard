# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-30 18:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Login',
            fields=[
                ('emp_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('emp_name', models.CharField(max_length=64)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Machines',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_id', models.CharField(max_length=255, unique=True)),
                ('machine_name', models.CharField(max_length=255, unique=True)),
                ('EmpId', models.ForeignKey(db_column='emp_id', on_delete=django.db.models.deletion.CASCADE, to='login.Login')),
            ],
        ),
    ]
