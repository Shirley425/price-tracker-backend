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

    user_id = (
        event
        .get("pathParameters", {})
        .get("user_id")
    )
    if not user_id:
    return {
            "statusCode": 400,
            "body": json.dumps({"error": "user_id is required"})
    }


    conn = get_connection()
    cur = conn.cursor()


    try:

        cur.execute(
            """
            SELECT
                tracked_item_id,
                product_title,
                provider,
                current_price,
                target_price,
                status,
                created_at
            FROM tracked_items
            WHERE user_id = %s;
            """,
            (user_id,)
        )


        rows = cur.fetchall()


        items = []


        for row in rows:

            items.append(
                {
                    "tracked_item_id": str(row[0]),
                    "product_title": row[1],
                    "provider": row[2],
                    "current_price": float(row[3])
                        if row[3] else None,
                    "target_price": float(row[4])
                        if row[4] else None,
                    "status": row[5],
                    "created_at": row[6].isoformat()
                }
            )


        return {
            "statusCode": 200,
            "body": json.dumps(items)
        }


    except Exception as e:

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