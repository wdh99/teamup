# Generated by Django 4.2.7 on 2023-12-10 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_alter_user_gender'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='user',
            new_name='owner',
        ),
        migrations.AddField(
            model_name='post',
            name='users',
            field=models.ManyToManyField(blank=True, to='api.user'),
        ),
    ]