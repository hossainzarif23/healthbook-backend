# Generated by Django 5.0.1 on 2024-02-23 04:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forum", "0010_alter_upvotepost_post"),
    ]

    operations = [
        migrations.AlterField(
            model_name="upvotepost",
            name="post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="forum.post"
            ),
        ),
    ]