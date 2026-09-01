# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WorkSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(auto_now_add=True, verbose_name='\u041d\u0430\u0447\u0430\u043b\u043e')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='\u041a\u043e\u043d\u0435\u0446')),
            ],
            options={
                'ordering': ['-start_time'],
                'verbose_name': '\u0421\u0435\u0441\u0441\u0438\u044f \u0440\u0430\u0431\u043e\u0442\u044b',
                'verbose_name_plural': '\u0421\u0435\u0441\u0441\u0438\u0438 \u0440\u0430\u0431\u043e\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='TimerSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('daily_goal_hours', models.FloatField(default=8.0, verbose_name='\u0426\u0435\u043b\u044c \u043d\u0430 \u0434\u0435\u043d\u044c (\u0447\u0430\u0441\u044b)')),
            ],
            options={
                'verbose_name': '\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0442\u0430\u0439\u043c\u0435\u0440\u0430',
                'verbose_name_plural': '\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0442\u0430\u0439\u043c\u0435\u0440\u0430',
            },
        ),
    ]
