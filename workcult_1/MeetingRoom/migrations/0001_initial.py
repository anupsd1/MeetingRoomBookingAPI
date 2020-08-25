# Generated by Django 3.0.5 on 2020-05-17 10:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('LocalUser', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlyUsage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.CharField(max_length=200)),
                ('used_this_month', models.FloatField(default=0)),
                ('used_till_date', models.FloatField(default=0, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='LocalUser.Company')),
            ],
        ),
        migrations.CreateModel(
            name='MeetingRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('allowed', models.BooleanField(default=False)),
                ('used_till_date', models.FloatField(default=0)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='LocalUser.Company')),
            ],
        ),
    ]