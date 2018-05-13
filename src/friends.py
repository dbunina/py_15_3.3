# from urllib.parse import urlencode
import requests

AUTH_URL = 'http://oauth.vk.com/authorize'
APP_ID = 6476738

# Понимаю, что подразумевалось использовать Implicit flow, но
# пришлось использовать https://vk.com/dev/authcode_flow_user, потому что токен не приходит,
# даже если в response-type указать token (все равно в ответе приходит code).
# Пробовала на нескольких приложениях, результат одинаковый (приходит code, а не access_token)
# Такая проблема существует, причины / решения не нашла :) Ссылку на SOF без ответа указала в комменте к домашке.
# Ключ доступа, полученный таким способом, не привязан к IP-адресу, поэтому вся sensitive data маскирована.

AUTH_DATA = {
    'client_id': APP_ID,
    'display': 'page',
    'scope': 'friends',
    'response-type': 'code',
    'v': '5.74'
}

# print('?'.join((AUTH_URL, urlencode(AUTH_DATA))))

ACCESS_TOKEN_URL = 'https://oauth.vk.com/access_token'

CODE = 'code_which_returned_from_blank.html'  # for security reasons
CLIENT_SECRET = 'client_key_from_vk_app_settings'  # for security reasons

ACCESS_TOKEN_DATA = {
    'client_id': APP_ID,
    'client_secret': CLIENT_SECRET,
    'code': CODE
}

# print('?'.join((ACCESS_TOKEN_URL, urlencode(ACCESS_TOKEN_DATA))))

ACCESS_TOKEN = 'some_access_token'  # for security reasons


def get_mutual_friends(user_ids):
    """
    Get VK's mutual (common) friends for the given set of users.
    :param user_ids: given set of VK users, who may have common friends
    :return: a dictionary of common friends, which contains of each user's id and VK page
    """
    if len(user_ids) < 2:
        raise Exception('There should be at least 2 users to search for common friends!')

    friend_ids = get_common_friend_ids(user_ids)
    return get_common_friends_with_urls(friend_ids)


def get_common_friend_ids(user_ids):
    data = get_response_json(
        'friends.getMutual',
        parameters=dict(
            source_uid=user_ids[0],
            target_uids=get_separated_string_list(user_ids[1:])
        )
    )

    common_friend_ids = set()

    for user in data['response']:
        common = user['common_friends']
        if len(common_friend_ids) == 0:
            common_friend_ids = set(common)
        else:
            common_friend_ids = common_friend_ids.intersection(common)

    return common_friend_ids


def get_response_json(method, parameters):
    params = dict(
        v='5.74',
        access_token=ACCESS_TOKEN
    )
    params.update(parameters)

    response = requests.get(
        'https://api.vk.com/method/{}'.format(method),
        params=params
    )
    return response.json()


def get_separated_string_list(int_list):
    return ','.join(str(x) for x in int_list)


def get_common_friends_with_urls(common_friend_ids):
    common_friends = dict()

    data = get_response_json(
        'users.get',
        parameters=dict(
            user_ids=get_separated_string_list(common_friend_ids),
            fields='domain'
        )
    )

    for user_data in data['response']:
        user_id = user_data['id']
        url = 'https://vk.com/{}'.format(user_data['domain'])
        common_friends[user_id] = url

    return common_friends


print(get_mutual_friends([1319072, 562624, 282339, 537825]))
