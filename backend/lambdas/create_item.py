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

    body = json.loads(event["body"])

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            INSERT INTO tracked_items
            (
                user_id,
                provider,
                external_id,
                product_title,
                product_url,
                image_url,
                target_price,
                current_price,
                status
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s)

            RETURNING tracked_item_id;
            """,
            (
                body["user_id"],
                body["provider"],
                body["external_id"],
                body["product_title"],
                body.get("product_url"),
                body.get("image_url"),
                body["target_price"],
                body.get("current_price"),
                "ACTIVE"
            )
        )


        item_id = cur.fetchone()[0]


        conn.commit()


        return {
            "statusCode": 201,
            "body": json.dumps(
                {
                    "tracked_item_id": str(item_id)
                }
            )
        }


    except Exception as e:

        conn.rollback()

        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": str(e)
                }
            )
        }


    finally:

        cur.close()