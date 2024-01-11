from pathlib import Path

import requests
import base64

from src.base_class.post import PostWall
from src.pars_conf import read_config


class WP_API():
    def __init__(self, url: str = None, user: str = None, password: str = None) -> None:
        if url and user and password:
            self.url = url
            self.__set_token(user, password)
            self.password = password
        else:
            wp_confid = read_config('wp')
            self.url = wp_confid['url']
            self.__set_token(wp_confid['user'], wp_confid['password'])
            self.password = wp_confid['password']

    def __set_token(self, user: str, password: str) -> None:
        credentials = user + ':' + password
        self.token = base64.b64encode(credentials.encode())

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        if 'headers' in kwargs:
            kwargs['headers'].update(
                {'Authorization': 'Basic ' + self.token.decode('utf-8')})
        else:
            kwargs['headers'] = {
                'Authorization': 'Basic ' + self.token.decode('utf-8')}
        url = self.__join_url(endpoint)
        return requests.get(url, **kwargs, timeout=15)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        if 'headers' in kwargs:
            kwargs['headers'].update(
                {'Authorization': 'Basic ' + self.token.decode('utf-8')})
        else:
            kwargs['headers'] = {
                'Authorization': 'Basic ' + self.token.decode('utf-8')}
        url = self.__join_url(endpoint)
        return requests.post(url, **kwargs, timeout=15)

    def apload_photo(self, img_path: Path) -> tuple:
        with open(img_path, 'rb') as f:
            data = f.read()
        filename = img_path.stem
        extension = img_path.suffix[1:]
        headers = {
            'cache-control': 'no-cache',
            'Content-Disposition': 'attachment; filename=%s' % filename,
            'Content-Type': f'image/{extension}'
        }
        endpoint = "media"
        resp = self.post(endpoint, data=data, headers=headers)
        if resp.status_code == 201:
            resp = resp.json()
            newID = resp.get('id')
            link = resp.get('guid').get("rendered")
        return (newID, link)

    def create_post(self, pw: PostWall) -> None:
        img = []
        for p in pw.photo:
            img.append(self.apload_photo(
                Path(pw.get_photo_dir(), f'{p}.jpeg')))
        width = ''
        img_html = ''
        if img:
            if len(img) > 2:
                width = 'width="45%"'
            img_html = ''.join([f'<a href="{i[1]}" target="_blank" rel=" noreferrer noopener">\
                <img {width} src="{i[1]}" alt=""/></a>'for i in img[1:]])

        post_html = f'<p>{pw.post_text}<p>\n \
                    {img_html}\n \
                    {self.__get_video_html(pw)}'
        post = {
            'title': pw.title,
            'status': 'publish',
            'content': post_html,
            'categories': [3],  # category ID
            'date': pw.date_post.isoformat(),
        }
        if img:
            post['featured_media'] = img[0][0]
        if 'поздравляем' in pw.title.lower():
            post['featured_media'] = 3804
        return self.post('posts', json=post)

    def __get_video_html(self, pw: PostWall) -> str:
        if not pw.video:
            return ''

        video = []
        for v in pw.video:
            width = ''
            height = ''
            if v['width']:
                scale = 600 / v['width']
                width = f'width="{str(round(v["width"] * scale))}px"'
                height = f'height="{str(round(v["height"] * scale))}px"'
            video.append(
                f'<iframe src="{v["url_player"]}" {width} {height}  frameborder="0" allowfullscreen="allowfullscreen"> </iframe>')
        return '\n'.join(video)

    def __join_url(self, endpoint: str) -> str:
        return '/'.join([self.url, 'wp-json/wp/v2', endpoint])


if __name__ == '__main__':
    wp = WP_API()
    res = wp.get('posts').json()[3]
    print(res)
