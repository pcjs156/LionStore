# Generated by Django 3.0.8 on 2020-07-24 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='image',
            field=models.ImageField(blank=True, upload_to='user_profile_image/', verbose_name='대표 이미지'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='introduce',
            field=models.TextField(verbose_name='소개글'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='nickname',
            field=models.CharField(max_length=15, verbose_name='닉네임/상호명'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='password_answer',
            field=models.CharField(max_length=30, verbose_name='비밀번호 찾기 답'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='password_question',
            field=models.CharField(choices=[('q1', '기억에 남는 추억의 장소는?'), ('q2', '자신의 인생 좌우명은?'), ('q3', '부모님의 결혼 기념일은?'), ('q4', '출신 초등학교는?'), ('q5', '소주 맥주 막걸리 중 가장 좋아하는 술은?')], max_length=30, verbose_name='비밀번호 찾기 질문'),
        ),
        migrations.AlterField(
            model_name='seller',
            name='telephone',
            field=models.CharField(max_length=20, verbose_name='판매자 연락처'),
        ),
        migrations.AlterField(
            model_name='stationer',
            name='latitude',
            field=models.DecimalField(decimal_places=6, max_digits=10, verbose_name='문방구 위치 위도'),
        ),
        migrations.AlterField(
            model_name='stationer',
            name='longitude',
            field=models.DecimalField(decimal_places=6, max_digits=10, verbose_name='문방구 위치 경도'),
        ),
        migrations.AlterField(
            model_name='webseller',
            name='link',
            field=models.CharField(max_length=200, verbose_name='웹 쇼핑몰 메인 주소'),
        ),
    ]