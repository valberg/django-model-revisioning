# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import doc_brown.models.single_table


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('char', models.CharField(null=True, max_length=255, blank=True)),
                ('int', models.IntegerField(null=True, blank=True)),
                ('text', models.TextField(null=True, blank=True)),
                ('boolean', models.BooleanField(default=False)),
                ('null_boolean', models.NullBooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, auto_now=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BarRevisions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('char', models.CharField(null=True, max_length=255, blank=True)),
                ('int', models.IntegerField(null=True, blank=True)),
                ('text', models.TextField(null=True, blank=True)),
                ('boolean', models.BooleanField(default=False)),
                ('null_boolean', models.NullBooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, auto_now=True)),
                ('revision_for', models.ForeignKey(to='testapp.Bar')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Foo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('revision_at', models.DateTimeField(auto_now_add=True)),
                ('is_revision', models.BooleanField(default=False)),
                ('char', models.CharField(null=True, max_length=255, blank=True)),
                ('int', models.IntegerField(null=True, blank=True)),
                ('text', models.TextField(null=True, blank=True)),
                ('boolean', models.BooleanField(default=False)),
                ('null_boolean', models.NullBooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, auto_now=True)),
                ('non_revisioned_foreign_key_serialized', models.TextField(verbose_name='non_revisioned_foreign_key_serialized', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NonRevisionedModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('char', models.CharField(null=True, max_length=255, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='foo',
            name='non_revisioned_foreign_key',
            field=models.ForeignKey(null=True, on_delete=doc_brown.models.single_table.revision_on_delete, to='testapp.NonRevisionedModel', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foo',
            name='revision_for',
            field=models.ForeignKey(null=True, related_name='revision_set', to='testapp.Foo', blank=True),
            preserve_default=True,
        ),
        migrations.AlterOrderWithRespectTo(
            name='foo',
            order_with_respect_to='revision_for',
        ),
    ]
