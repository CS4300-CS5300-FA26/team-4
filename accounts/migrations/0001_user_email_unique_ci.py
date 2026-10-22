from django.db import migrations

def create_email_index(apps, schema_editor):
    connection = schema_editor.connection

    # This migration supports SQLite and PostgreSQL only.
    if connection.vendor not in {"sqlite", "postgresql"}:
        raise RuntimeError(
            "Case-insensitive email uniqueness requires SQLite "
            "or PostgreSQL. The current database backend is "
            f"{connection.vendor!r}."
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
        details = ", ".join(
            f"{email!r} ({count} accounts)"
            for email, count in duplicates
        )
        raise RuntimeError(
            "Cannot create the case-insensitive email index because "
            "duplicate email addresses already exist. Resolve these "
            f"conflicts and rerun the migration: {details}"
        )

    schema_editor.execute("""
        CREATE UNIQUE INDEX unique_auth_user_email_ci
        ON auth_user (LOWER(email))
        WHERE email <> ''
    """)


def drop_email_index(apps, schema_editor):
    if schema_editor.connection.vendor not in {"sqlite", "postgresql"}:
        return

    schema_editor.execute(
        "DROP INDEX IF EXISTS unique_auth_user_email_ci"
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