from oasst_backend.config import Settings


def test_create_default_settings():
    """
    Make sure we can create one of these
    """
    Settings()


def test_construct_db_uri_from_dict():
    """
    No URI provided? Construct one from the other settings
    """

    settings = Settings(
        POSTGRES_USER="myuser",
        POSTGRES_PASSWORD="weak_password",
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=54321,
        POSTGRES_DB="mydb",
    )

    assert str(settings.DATABASE_URI) == "postgresql://myuser:weak_password@localhost:54321/mydb"


def test_connection_string():
    """
    If we provide a connection string, use that
    """

    settings = Settings(DATABASE_URI="postgresql://myuser:weak_password@localhost:54321/mydb")

    assert str(settings.DATABASE_URI) == "postgresql://myuser:weak_password@localhost:54321/mydb"


def test_task_expiry_time():
    """
    Should be two days
    """
    settings = Settings()

    two_days_in_minutes = 60 * 24 * 2

    assert settings.TASK_VALIDITY_MINUTES == two_days_in_minutes
