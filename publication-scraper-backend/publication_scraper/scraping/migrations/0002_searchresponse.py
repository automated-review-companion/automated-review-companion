# Generated by Django 4.2.14 on 2024-09-08 04:32

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchResponse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('query', models.JSONField()),
                ('variations', models.JSONField()),
                ('matches', models.JSONField()),
                ('results', models.JSONField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
