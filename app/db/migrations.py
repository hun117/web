from sqlalchemy import Engine, inspect, text


def migrate_user_table(engine: Engine) -> None:
    """Make email and password nullable while preserving the legacy SQLite rows."""
    if engine.dialect.name != "sqlite":
        raise RuntimeError("The user table migration currently supports SQLite only")

    with engine.begin() as connection:
        if "user" not in inspect(connection).get_table_names():
            return

        columns = {
            column["name"]: column
            for column in connection.execute(text("PRAGMA table_info(user)")).mappings()
        }
        if not columns:
            return
        if not columns.get("email", {}).get("notnull") and not columns.get("password", {}).get("notnull"):
            return

        connection.execute(text(
            "CREATE TABLE user__new ("
            "idx INTEGER NOT NULL PRIMARY KEY, "
            "email VARCHAR NULL, "
            "password VARCHAR NULL, "
            "name VARCHAR NOT NULL)"
        ))
        connection.execute(text(
            "INSERT INTO user__new (idx, email, password, name) "
            "SELECT idx, email, password, name FROM user"
        ))
        connection.execute(text("DROP TABLE user"))
        connection.execute(text("ALTER TABLE user__new RENAME TO user"))
