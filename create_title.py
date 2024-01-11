from datetime import datetime, timezone
from sys import argv
from psycopg2 import sql

from src.db_connect import DB
from src.parse_arg_cl import parse_argcl


START_DATE = None
#START_DATE = datetime.strptime('17.12.23', '%d.%m.%y').replace(tzinfo=timezone.utc)

if not START_DATE:
    START_DATE = parse_argcl(argv)[0]

if START_DATE:
    db = DB()
    query = sql.SQL('SELECT id, post_text \
                    FROM post \
                    WHERE date_post >= %(start_date)s\
                    ORDER BY date_post')
    ids_post = db.get_data(query, {'start_date': START_DATE})

    all_count = len(ids_post)
    i = 0
    for p in ids_post:
        i += 1
        print(
            f'----------------------- {i} пост из {all_count} -------------------------------')
        print(p[1])

        title = input("Введите заголовок: ")
        re = db.get_data(sql.SQL('UPDATE post \
                        SET title = %(title)s \
                        WHERE  id = %(id)s        '
                                 ), {'title': title, 'id': p[0]})
