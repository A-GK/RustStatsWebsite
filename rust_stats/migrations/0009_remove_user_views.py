# Generated by Django 3.0.6 on 2020-06-25 18:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rust_stats', '0008_user_account_created'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='views',
        ),
    ]
