# Generated by Django 3.0.8 on 2020-08-13 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0002_product_registerdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='totalScore',
            field=models.DecimalField(decimal_places=1, max_digits=2, null=True, verbose_name='총점'),
        ),
    ]