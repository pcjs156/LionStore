# Generated by Django 3.0.8 on 2020-08-04 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='reviewImage2',
            field=models.ImageField(null=True, upload_to='review_image/', verbose_name='리뷰 이미지2'),
        ),
    ]
