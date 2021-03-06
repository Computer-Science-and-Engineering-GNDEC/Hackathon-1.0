# Generated by Django 2.2.10 on 2021-03-06 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20210306_0101'),
    ]

    operations = [
        migrations.CreateModel(
            name='person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('in_persons', models.PositiveIntegerField(default=0)),
                ('out_persons', models.PositiveIntegerField(default=0)),
                ('total_persons', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='item',
            name='item',
            field=models.CharField(choices=[('school bag', 'SCHOOL BAG'), ('hand bag', 'HAND BAG'), ('travelling bag', 'TRAVELLING BAG')], default='schoolbag', max_length=20),
        ),
    ]