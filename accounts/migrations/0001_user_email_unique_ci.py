from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

# prevent duplicate email addresses
    operations = [
        migrations.RunSQL(
            sql="""
                CREATE UNIQUE INDEX unique_auth_user_email_ci
                ON auth_user (LOWER(email))
                WHERE email <> '';
            """,
            reverse_sql="""
                DROP INDEX unique_auth_user_email_ci;
            """,
        ),
    ]