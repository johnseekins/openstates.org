# Generated by Django 3.2 on 2021-06-21 18:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("people_admin", "0007_personretirement"),
    ]

    operations = [
        migrations.CreateModel(
            name="NewPerson",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.TextField()),
                ("state", models.TextField()),
                ("district", models.TextField()),
                ("chamber", models.TextField()),
                (
                    "delta_set",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="person_addition",
                        to="people_admin.deltaset",
                    ),
                ),
            ],
        ),
    ]
