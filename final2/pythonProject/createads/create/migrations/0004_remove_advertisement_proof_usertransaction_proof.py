# Generated by Django 5.0.6 on 2024-06-29 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('create', '0003_advertisement_proof'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advertisement',
            name='proof',
        ),
        migrations.AddField(
            model_name='usertransaction',
            name='proof',
            field=models.TextField(blank=True, null=True),
        ),
    ]
