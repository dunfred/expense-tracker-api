# Generated by Django 4.1.7 on 2023-03-25 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_expenditure_timestamp_income_timestamp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='expenditure',
            old_name='timestamp',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='income',
            old_name='timestamp',
            new_name='created_at',
        ),
        migrations.AddField(
            model_name='expenditure',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='income',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
