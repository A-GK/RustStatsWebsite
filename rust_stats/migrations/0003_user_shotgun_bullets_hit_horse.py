# Generated by Django 3.0.6 on 2020-06-16 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rust_stats', '0002_user_hours_played'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='shotgun_bullets_hit_horse',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
