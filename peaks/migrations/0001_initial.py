# Generated by Django 4.1.5 on 2023-02-07 19:51

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Country",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=15)),
                ("slug", models.SlugField(blank=True, max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name="Peak",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("slug", models.SlugField(blank=True, max_length=80)),
                ("wiki", models.CharField(blank=True, max_length=80)),
                ("name", models.CharField(max_length=80)),
                ("alias", models.CharField(blank=True, max_length=30, null=True)),
                ("name_en", models.CharField(blank=True, max_length=50, null=True)),
                ("name_de", models.CharField(blank=True, max_length=50, null=True)),
                ("name_fr", models.CharField(blank=True, max_length=50, null=True)),
                ("name_it", models.CharField(blank=True, max_length=50, null=True)),
                ("name_sl", models.CharField(blank=True, max_length=50, null=True)),
                ("name_ch", models.CharField(blank=True, max_length=50, null=True)),
                ("name_de_AT", models.CharField(blank=True, max_length=50, null=True)),
                ("name_de_DE", models.CharField(blank=True, max_length=50, null=True)),
                ("alt_name", models.CharField(blank=True, max_length=70, null=True)),
                ("lat", models.FloatField()),
                ("lon", models.FloatField()),
                ("ele", models.FloatField(null=True)),
                ("prominence", models.IntegerField(blank=True, null=True)),
                ("neargtdelta", models.FloatField(null=True)),
                ("neargtdist", models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Region",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=65)),
                ("slug", models.SlugField(blank=True, max_length=65)),
            ],
        ),
        migrations.CreateModel(
            name="Tour",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.TextField(blank=True)),
                ("date", models.DateField(blank=True)),
                ("heading", models.CharField(blank=True, max_length=255, null=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "likedby",
                    models.ManyToManyField(
                        blank=True,
                        default="",
                        related_name="liked_tours",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "peak",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tours",
                        to="peaks.peak",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tours",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="region",
            index=models.Index(fields=["slug"], name="peaks_regio_slug_7034c3_idx"),
        ),
        migrations.AddField(
            model_name="peak",
            name="neargt",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="nearestlower",
                to="peaks.peak",
            ),
        ),
        migrations.AddField(
            model_name="peak",
            name="region",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="peaks",
                to="peaks.region",
            ),
        ),
        migrations.AddField(
            model_name="country",
            name="peaks",
            field=models.ManyToManyField(related_name="countries", to="peaks.peak"),
        ),
        migrations.AddField(
            model_name="user",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.AddIndex(
            model_name="peak",
            index=models.Index(
                fields=[
                    "name",
                    "alias",
                    "name_en",
                    "name_de",
                    "name_fr",
                    "name_it",
                    "name_sl",
                    "name_ch",
                    "name_de_AT",
                    "name_de_DE",
                    "alt_name",
                ],
                name="peaks_peak_name_a338d4_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="peak",
            index=models.Index(fields=["region"], name="peaks_peak_region__1a280b_idx"),
        ),
        migrations.AddIndex(
            model_name="peak",
            index=models.Index(fields=["slug"], name="peaks_peak_slug_84a725_idx"),
        ),
    ]
