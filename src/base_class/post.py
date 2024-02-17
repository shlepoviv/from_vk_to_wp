from pathlib import Path

import requests
from psycopg2 import sql
from src.scheme import SchPostWall
from src.db_connect import DB


class PostWall:
    list_felds_in_table_post = ['id', 'owner_id',
                                'date_post', 'post_text', 'title', 'post_source']

    def __init__(self) -> None:
        self.id = None
        self.owner_id = None
        self.date_post = None
        self.photo = []
        self.video = []
        self.post_text = None
        self.title = None
        self.post_source = None

    @staticmethod
    def load_from_api(resp: dict):
        br = SchPostWall.model_validate(resp)

        res = PostWall()

        res.id = br.id
        res.owner_id = br.owner_id
        res.date_post = br.date
        res.post_text = br.text
        res.post_source = f'{br.post_source.type}{br.post_source.platform}'

        for attachment in br.attachments:
            if attachment.type == 'photo':
                for s in attachment.photo.sizes:
                    if s.type == 'z':
                        res.load_photo(s.url, attachment.photo.id)
                        res.photo.append(attachment.photo.id)
            if attachment.type == 'video':
                res.video.append({'id_video': f'{attachment.video.owner_id}_{attachment.video.id}_{attachment.video.access_key}',
                                  'url_player': '',
                                  'width': 0,
                                  'height': 0})
        return res

    @staticmethod
    def load_from_db(id_post: int):
        
        resp = PostWall.load_post_fromdb(id_post)
        if resp:
            post = PostWall()

            for i in range(len(post.list_felds_in_table_post)):
                setattr(post, post.list_felds_in_table_post[i], resp[0][i])

            post.load_photo_fromdb()
            post.load_video_fromdb()

            return post

    
    @staticmethod
    def load_post_fromdb(id_post):
        db = DB()
        query = sql.SQL('SELECT {felds} \
                        FROM post \
                        WHERE id = %(id)s').format(felds=sql.SQL(',').join(map(sql.Identifier, PostWall.list_felds_in_table_post)))
        return db.get_data(query, {'id': id_post})
                
    def load_photo_fromdb(self):
        self.photo.clear()
        db = DB()
        query = sql.SQL('SELECT id_photo \
                        FROM photo \
                        WHERE owner_id = %(owner_id)s')
        resp = db.get_data(query, {'owner_id': self.id})
        if resp:
            for i in resp:
                self.photo.append(i[0])

    def load_video_fromdb(self):
        self.video.clear()
        db = DB()
        query = sql.SQL('SELECT id_video, url_player ,width,height\
                        FROM video \
                        WHERE owner_id = %(owner_id)s')
        resp = db.get_data(query, {'owner_id': self.id})
        if resp:
            for i in resp:
                self.video.append(
                    {'id_video': i[0], 'url_player': i[1], 'width': i[2], 'height': i[3]})

    def write_to_db(self) -> None:
        db = DB()

        if not PostWall.load_post_fromdb(self.id):
            query = db.get_insert_query('post', self.list_felds_in_table_post)
            param = dict({(i, self.__dict__[i])
                        for i in self.list_felds_in_table_post})
            db.get_data(query, param)
            if self.photo:
                self._write_photo_to_db()
            if self.video:
                self._write_video_to_db()

    def _write_photo_to_db(self) -> None:
        db = DB()
        list_felds = ['id_photo', 'owner_id']
        query = db.get_insert_query('photo', list_felds)
        list_param = []
        for p in self.photo:
            list_param.append({'id_photo': p, 'owner_id': self.id})
        db.get_data(query, list_param)

    def _write_video_to_db(self) -> None:
        db = DB()
        list_felds = ['id_video', 'url_player', 'owner_id', 'width', 'height']
        query = db.get_insert_query('video', list_felds)
        list_param = []
        for v in self.video:
            list_param.append(v | {'owner_id': self.id})
        db.get_data(query, list_param)

    def load_photo(self, url: str, id_photo: int) -> None:
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            if resp.headers['Content-Type'] == 'image/jpeg':
                with open(Path(self.get_photo_dir(), f'{id_photo}.jpeg'), 'wb') as f:
                    f.write(resp.content)

    def get_photo_dir(self) -> Path:
        DATA_DIR = 'data'
        dd = Path(Path.cwd(), DATA_DIR)
        if not dd.exists() or not dd.is_dir():
            dd.mkdir()
        dd = Path(dd, str(self.id))
        if not dd.exists() or not dd.is_dir():
            dd.mkdir()
        return dd

    @property
    def check(self):
        return bool(self.id) and bool(self.date_post) and bool(self.post_text) and bool(self.title)


if __name__ == '__main__':
    ab = PostWall()
    print(ab.load_post_fromdb(1))