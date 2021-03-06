# Generated by Django 3.0.8 on 2020-08-26 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20200825_1324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='age',
            field=models.CharField(choices=[('etcs', '기타'), ('10s', '10대'), ('20s', '20대'), ('30s', '30대')], default='etcs', max_length=5, null=True, verbose_name='연령대'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='job',
            field=models.CharField(choices=[('J0', '기타'), ('J1', '학생'), ('J2', '아티스트')], default='J0', max_length=10, null=True, verbose_name='직업'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='penInterest_1',
            field=models.CharField(choices=[('P0', '기타'), ('P1', '볼펜'), ('P2', '연필'), ('P3', '색연필'), ('P4', '만년필'), ('P5', '샤프펜슬'), ('P6', '형광펜'), ('P7', '유성펜'), ('P8', '젤펜')], default='P0', max_length=10, null=True, verbose_name='관심 펜 1순위'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='penInterest_2',
            field=models.CharField(choices=[('P0', '기타'), ('P1', '볼펜'), ('P2', '연필'), ('P3', '색연필'), ('P4', '만년필'), ('P5', '샤프펜슬'), ('P6', '형광펜'), ('P7', '유성펜'), ('P8', '젤펜')], default='P0', max_length=10, null=True, verbose_name='관심 펜 2순위'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='penInterest_3',
            field=models.CharField(choices=[('P0', '기타'), ('P1', '볼펜'), ('P2', '연필'), ('P3', '색연필'), ('P4', '만년필'), ('P5', '샤프펜슬'), ('P6', '형광펜'), ('P7', '유성펜'), ('P8', '젤펜')], default='P0', max_length=10, null=True, verbose_name='관심 펜 3순위'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='usage',
            field=models.CharField(choices=[('U0', '기타'), ('U1', '공부/필기'), ('U2', '문서 작성'), ('U3', '드로잉'), ('U4', '다이어리 꾸미기'), ('U5', '캘리그라피')], default='U0', max_length=20, null=True, verbose_name='주 사용 용도'),
        ),
    ]
