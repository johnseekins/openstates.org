# Generated by Django 2.2.19 on 2021-03-08 16:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("people_admin", "0002_deltaset_persondelta"),
    ]

    operations = [
        migrations.AddField(
            model_name="deltaset",
            name="pr_status",
            field=models.CharField(
                choices=[
                    ("N", "Not Created"),
                    ("C", "Created"),
                    ("M", "Merged"),
                    ("R", "Rejected"),
                ],
                default="N",
                max_length=1,
            ),
        ),
    ]
