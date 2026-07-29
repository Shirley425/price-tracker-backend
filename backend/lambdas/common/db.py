import os
import psycopg2


connection = None


def get_connection():

    global connection

    if connection is None or connection.closed:

        connection = psycopg2.connect(
            host=os.environ["DB_HOST"],
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            port=os.environ.get("DB_PORT", 5432)
        )

    return connection