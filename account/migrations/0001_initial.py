# Generated by Django 3.0.8 on 2020-07-27 14:59

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_Customer', models.BooleanField(default=False, verbose_name='customer status')),
                ('is_WebSeller', models.BooleanField(default=False, verbose_name='webSeller status')),
                ('is_Stationer', models.BooleanField(default=False, verbose_name='stationer status')),
                ('nickname', models.CharField(max_length=15, verbose_name='닉네임/상호명')),
                ('image', models.ImageField(blank=True, upload_to='user_profile_image/', verbose_name='대표 이미지')),
                ('introduce', models.TextField(verbose_name='소개글')),
                ('telephone', models.CharField(default='', max_length=20, verbose_name='판매자 연락처')),
                ('link', models.CharField(default='', max_length=200, verbose_name='웹 쇼핑몰 메인 주소')),
                ('latitude', models.DecimalField(decimal_places=6, default=0, max_digits=10, verbose_name='문방구 위치 위도')),
                ('longitude', models.DecimalField(decimal_places=6, default=0, max_digits=10, verbose_name='문방구 위치 경도')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
