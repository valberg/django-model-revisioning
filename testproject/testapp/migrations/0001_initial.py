# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Foo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('revision_at', models.DateTimeField(auto_now_add=True)),
                ('is_revision', models.BooleanField(default=False)),
                ('char', models.CharField(max_length=255, blank=True, null=True)),
                ('int', models.IntegerField(blank=True, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('boolean', models.BooleanField(default=False)),
                ('null_boolean', models.NullBooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('revision_for', models.ForeignKey(to='testapp.Foo', blank=True, null=True, related_name='revision_set')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterOrderWithRespectTo(
            name='foo',
            order_with_respect_to='revision_for',
        ),
    ]
