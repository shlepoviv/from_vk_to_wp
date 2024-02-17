from datetime import datetime, timezone
from sys import argv
from psycopg2 import sql

from src.base_class.post import  PostWall
from src.db_connect import DB
from src.parse_arg_cl import parse_argcl
from src.wp_api.wp_api import WP_API

START_DATE = None
START_DATE = datetime.strptime('09.02.24', '%d.%m.%y').replace(tzinfo=timezone.utc)

if not START_DATE:
    START_DATE = parse_argcl(argv)[0]

if START_DATE:
    db = DB()
    query = sql.SQL("SELECT id \
                    FROM post \
                    WHERE title <> ''\
                    AND date_post >= %(start_date)s\
                    ORDER BY date_post")
    ids_post = db.get_data(query,{'start_date':START_DATE})

    wp = WP_API()

    all_post = len(ids_post)
    created = 0
    for idp in ids_post:
        br = PostWall.load_from_db(idp[0])
        if br.check:        
            resp = wp.create_post(br)
            if resp.status_code == 201:
                created += 1               
        
    print(f'Loaded from database {all_post}, posted on site {created}.')

    