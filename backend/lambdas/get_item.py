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


def resolve_user_id(event, conn, cur):
    claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
    sub = claims["sub"]
    email = claims.get("email")

    cur.execute(
        "SELECT user_id FROM users WHERE cognito_sub = %s;",
        (sub,)
    )
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute(
        """
        UPDATE users
        SET cognito_sub = %s
        WHERE email = %s AND cognito_sub IS NULL
        RETURNING user_id;
        """,
        (sub, email)
    )
    row = cur.fetchone()
    if row:
        conn.commit()
        return row[0]

    cur.execute(
        """
        INSERT INTO users (user_id, cognito_sub, email, created_at)
        VALUES (gen_random_uuid(), %s, %s, NOW())
        RETURNING user_id;
        """,
        (sub, email)
    )
    user_id = cur.fetchone()[0]
    conn.commit()
    return user_id


def lambda_handler(event, context):
    conn = get_connection()
    cur = conn.cursor()
    try:
        user_id = resolve_user_id(event, conn, cur)

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
        conn.rollback()
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    finally:
        cur.close()
