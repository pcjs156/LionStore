# Generated by Django 3.0.8 on 2020-08-05 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='likeCount',
            field=models.PositiveIntegerField(default=0, verbose_name='좋아요 수'),
        ),
        migrations.AlterField(
            model_name='review',
            name='likeCount',
            field=models.PositiveIntegerField(default=0, verbose_name='좋아요 수'),
        ),
    ]