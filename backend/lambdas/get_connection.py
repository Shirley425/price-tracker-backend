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
            password=os.environ["DB_PASSWORD"]
        )

    return connection


def lambda_handler(event, context):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT version();")

    result = cursor.fetchone()

    cursor.close()

    return {
        "statusCode": 200,
        "body": str(result)
    }
