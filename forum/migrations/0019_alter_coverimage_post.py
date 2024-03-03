# Generated by Django 5.0.1 on 2024-03-03 06:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forum", "0018_remove_coverimage_image_remove_image_image_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coverimage",
            name="post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cover_images",
                to="forum.post",
            ),
        ),
    ]