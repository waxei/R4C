# Generated by Django 5.1.4 on 2024-12-15 19:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('robot_serial', models.CharField(max_length=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.customer')),
            ],
        ),
    ]