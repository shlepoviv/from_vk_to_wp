from datetime import datetime, timezone
from sys import argv

import vk_api
from vk_api.utils import enable_debug_mode
from src.base_class.post import PostWall
from src.pars_conf import read_config
from src.parse_arg_cl import parse_argcl

def __auth_handler():
    # Two-factor authentication code
    key = input("Enter authentication code: ")
    remember_device = True
    return key, remember_device


__debug_mode = False
start_date = None
start_date = datetime.strptime('17.12.23', '%d.%m.%y').replace(tzinfo=timezone.utc)

if not start_date:
    parsed_arg = parse_argcl(argv)
    start_date = parsed_arg[0]
    __debug_mode = parsed_arg[1]
else:
    __debug_mode = True


if start_date:
    vk_session = vk_api.VkApi(**read_config('vk'), auth_handler=__auth_handler)

    if __debug_mode:
        enable_debug_mode(vk_session)

    vk_session.auth()

    vk = vk_session.get_api()

    stop = False
    counter_all_post = 0
    counter_written_post = 0

    while not stop:
        resp = vk.wall.get(**read_config('vk_group'),
                           count=1, offset=counter_all_post)
        counter_all_post += 1
        if 'copy_history' in resp['items'][0]:
            item = resp['items'][0]['copy_history'][0]
        else:
            item = resp['items'][0]

        if item["inner_type"] != "wall_wallpost":
            continue

        post = PostWall.load_from_api(item)

        if post.video:
            for v in post.video:
                resp = vk.video.get(videos=v['id_video'])
                v['url_player'] = resp['items'][0]['player']
                v['width'] = resp['items'][0]['width']
                v['height'] = resp['items'][0]['height']

        if post.date_post < start_date:
            stop = True
        if post.post_source == 'api':
            continue
        post.write_to_db()
        counter_written_post += 1
    print(
        f'Parse {counter_all_post} posr, {counter_written_post} written in base.')
