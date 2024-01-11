from pathlib import Path

import psycopg2
from psycopg2 import sql

from src.pars_conf import read_config


class DB():

    def __init__(self, connect_param: dict = None) -> None:
        if connect_param:
            self.connect_param = connect_param
        else:
            self.connect_param = read_config('db')

    def get_data(self, query: str, params: dict = None):
        res = None
        with psycopg2.connect(**self.connect_param) as conn:
            with conn.cursor() as curs:
                if not params:
                    curs.execute(query)
                elif isinstance(params, dict):
                    curs.execute(query, params)
                else:
                    curs.executemany(query, params)
                if curs.rowcount > 0 and curs.statusmessage.startswith('SELECT'):
                    res = curs.fetchall()
        return res

    def create_tables(self, init_query: str = None) -> list:
        if not init_query:
            with open(Path('init', 'init_db_vk_wall.sql'), 'r', encoding='utf-8') as f:
                init_query = sql.SQL(f.read()).format()
        self.get_data(init_query)

    def get_db_tables(self) -> list:
        responce = self.get_data('SELECT table_name FROM information_schema.tables\
                                WHERE table_schema=%(table_schema)s', {'table_schema': 'public'})
        if responce:
            return [row[0] for row in responce]
        return []

    def get_columns_in_tabele(self, name_table: str) -> list:
        return [row[0] for row in (self.get_data('SELECT column_name \
        FROM information_schema.columns\
        WHERE table_schema = %(table_schema)s\
        AND table_name   = %(name_table)s', {'table_schema': 'public', 'name_table': name_table}))]

    def get_insert_query(self, name_table: str, list_fields: list[str]) -> str:
        query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({placeholder}) ").format(
            table=sql.Identifier(name_table),
            fields=sql.SQL(',').join(map(sql.Identifier, list_fields)),
            placeholder=sql.SQL(', ').join(map(sql.Placeholder, list_fields)))
        return query


if __name__ == '__main__':
    _db = DB()
    print(_db.get_db_tables())
    print(_db.create_tables())
    print(_db.get_db_tables())
