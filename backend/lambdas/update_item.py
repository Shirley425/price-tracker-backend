import json
from common.db import get_connection


def lambda_handler(event, context):

    item_id = (
        event["pathParameters"]
        ["tracked_item_id"]
    )


    body = json.loads(event["body"])


    conn = get_connection()
    cur = conn.cursor()


    try:


        cur.execute(
            """
            UPDATE tracked_items

            SET
                target_price=%s,
                status=%s

            WHERE tracked_item_id=%s;
            """,

            (
                body["target_price"],
                body["status"],
                item_id
            )
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