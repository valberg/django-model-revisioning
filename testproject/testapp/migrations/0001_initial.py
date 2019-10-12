# Generated by Django 2.2.5 on 2019-10-12 07:35
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models

import model_history.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0011_update_proxy_permissions"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Bar",
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
                ("char", models.CharField(blank=True, max_length=255, null=True)),
                ("int", models.IntegerField(blank=True, null=True)),
                ("text", models.TextField(blank=True, null=True)),
                ("boolean", models.BooleanField(default=False)),
                ("null_boolean", models.NullBooleanField()),
                (
                    "hello_world",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Baz",
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
                ("char", models.CharField(blank=True, max_length=255, null=True)),
                ("int", models.IntegerField(blank=True, null=True)),
                ("text", models.TextField(blank=True, null=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Foo",
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
                ("char", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="ModelWithoutOptions",
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
                ("content", models.TextField()),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="NonRevisionedModel",
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
                ("char", models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="SoftDeleted",
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
                ("content", models.TextField()),
                ("is_deleted", models.NullBooleanField(default=False)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="SoftDeletedRevision",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("revision_at", models.DateTimeField(auto_now_add=True)),
                ("is_head", models.BooleanField(default=False)),
                ("content", models.TextField()),
                (
                    "original_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="revisions",
                        to="testapp.SoftDeleted",
                    ),
                ),
                (
                    "parent_revision",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children_revisions",
                        to="testapp.SoftDeletedRevision",
                    ),
                ),
            ],
            options={"ordering": ["revision_at"], "abstract": False},
        ),
        migrations.CreateModel(
            name="ModelWithoutOptionsRevision",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("revision_at", models.DateTimeField(auto_now_add=True)),
                ("is_head", models.BooleanField(default=False)),
                ("content", models.TextField()),
                (
                    "original_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="revisions",
                        to="testapp.ModelWithoutOptions",
                    ),
                ),
                (
                    "parent_revision",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children_revisions",
                        to="testapp.ModelWithoutOptionsRevision",
                    ),
                ),
            ],
            options={"ordering": ["revision_at"], "abstract": False},
        ),
        migrations.CreateModel(
            name="FooRevision",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("revision_at", models.DateTimeField(auto_now_add=True)),
                ("is_head", models.BooleanField(default=False)),
                ("char", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "original_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="revisions",
                        to="testapp.Foo",
                    ),
                ),
                (
                    "parent_revision",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children_revisions",
                        to="testapp.FooRevision",
                    ),
                ),
            ],
            options={"ordering": ["revision_at"], "abstract": False},
        ),
        migrations.CreateModel(
            name="BazRevision",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("revision_at", models.DateTimeField(auto_now_add=True)),
                ("is_head", models.BooleanField(default=False)),
                ("char", models.CharField(blank=True, max_length=255, null=True)),
                ("text", models.TextField(blank=True, null=True)),
                (
                    "original_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="revisions",
                        to="testapp.Baz",
                    ),
                ),
                (
                    "parent_revision",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children_revisions",
                        to="testapp.BazRevision",
                    ),
                ),
            ],
            options={"ordering": ["revision_at"], "abstract": False},
        ),
        migrations.CreateModel(
            name="BarRevision",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("revision_at", models.DateTimeField(auto_now_add=True)),
                ("is_head", models.BooleanField(default=False)),
                ("char", models.CharField(blank=True, max_length=255, null=True)),
                ("int", models.IntegerField(blank=True, null=True)),
                ("text", models.TextField(blank=True, null=True)),
                ("boolean", models.BooleanField(default=False)),
                ("null_boolean", models.NullBooleanField()),
                (
                    "hello_world",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "foo",
                    model_history.fields.RevisionedForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="testapp.FooRevision",
                    ),
                ),
                (
                    "groups",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="auth.Group",
                    ),
                ),
                (
                    "non_revisioned_foreign_key",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="testapp.NonRevisionedModel",
                    ),
                ),
                (
                    "original_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="revisions",
                        to="testapp.Bar",
                    ),
                ),
                (
                    "parent_bar",
                    model_history.fields.RevisionedForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="testapp.BarRevision",
                    ),
                ),
                (
                    "parent_revision",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children_revisions",
                        to="testapp.BarRevision",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["revision_at"], "abstract": False},
        ),
        migrations.AddField(
            model_name="bar",
            name="foo",
            field=model_history.fields.RevisionedForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="testapp.Foo",
            ),
        ),
        migrations.AddField(
            model_name="bar",
            name="groups",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="auth.Group",
            ),
        ),
        migrations.AddField(
            model_name="bar",
            name="non_revisioned_foreign_key",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="testapp.NonRevisionedModel",
            ),
        ),
        migrations.AddField(
            model_name="bar",
            name="parent_bar",
            field=model_history.fields.RevisionedForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="testapp.Bar",
            ),
        ),
        migrations.AddField(
            model_name="bar",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
