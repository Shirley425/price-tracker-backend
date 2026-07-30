import json
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

    item_id = (
        event["pathParameters"]
        ["tracked_item_id"]
    )


    conn = get_connection()
    cur = conn.cursor()


    try:

        cur.execute(
            """
            DELETE FROM tracked_items

            WHERE tracked_item_id=%s;
            """,
            (item_id,)
        )


        conn.commit()


        return {
            "statusCode":204,
            "body":""
        }



    except Exception as e:

        conn.rollback()

        return {
            "statusCode":500,
            "body":json.dumps(
                {
                    "error":str(e)
                }
            )
        }



    finally:

        cur.close()