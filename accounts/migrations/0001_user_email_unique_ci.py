from django.conf import settings
from django.db import migrations


INDEX_NAME = "unique_auth_user_email_ci"


def create_email_index(apps, schema_editor):
    connection = schema_editor.connection

    # This migration supports SQLite and PostgreSQL only.
    if connection.vendor not in {"sqlite", "postgresql"}:
        raise RuntimeError(
            "Case-insensitive email uniqueness requires SQLite "
            "or PostgreSQL. The current database backend is "
            f"{connection.vendor!r}."
        )

    # This migration specifically targets Django's default User model.
    if settings.AUTH_USER_MODEL != "auth.User":
        raise RuntimeError(
            "This migration supports Django's default auth.User model "
            "only. A custom AUTH_USER_MODEL requires a separate "
            "migration targeting its database table."
        )

    # Check for conflicting email addresses before creating the index.
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT LOWER(email), COUNT(*)
            FROM auth_user
            WHERE email <> ''
            GROUP BY LOWER(email)
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()

    if duplicates:
        duplicate_groups = len(duplicates)
        affected_accounts = sum(count for _, count in duplicates)

        raise RuntimeError(
            "Cannot create the case-insensitive email index because "
            f"{duplicate_groups} duplicate email group(s) involving "
            f"{affected_accounts} accounts were found. "
            "Resolve the conflicts using a secure, authorized database "
            "investigation, then rerun the migration. Email addresses "
            "are intentionally omitted from this error message."
        )

    schema_editor.execute(f"""
        CREATE UNIQUE INDEX {INDEX_NAME}
        ON auth_user (LOWER(email))
        WHERE email <> ''
    """)


def drop_email_index(apps, schema_editor):
    if schema_editor.connection.vendor not in {"sqlite", "postgresql"}:
        return

    schema_editor.execute(
        f"DROP INDEX IF EXISTS {INDEX_NAME}"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(
            create_email_index,
            reverse_code=drop_email_index,
        ),
    ]