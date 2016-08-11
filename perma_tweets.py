from datetime import datetime
from datetime import timedelta
import requests

PERMA_API_KEY = "123"
PERMA_BASE_API = "https://api.perma-stage.org/v1"
PERMA_API_URL = "%s/public/archives?api_key=%s" % (PERMA_BASE_API, PERMA_API_KEY)

TWITTER_BASE_URL = "https://twitter.com/search"

global root_folder_id

def get_folder_id(name):
    url = "%s/user/folders/?api_key=%s" % (PERMA_BASE_API, PERMA_API_KEY)
    response = requests.get(url)

    for folder in response.json()['objects']:
        if folder['name'] == name:
            return folder['id']
    raise Exception('No such folder exists')

def set_root_folder(name):
    global root_folder_id
    folder_id = get_folder_id(name)
    root_folder_id = folder_id

def create_weekly_ranges(from_date, to_date):
    # TODO: not sure if range is inclusive
    # name collection using handle
    # TODO: figure out an optimal range. Is it weekly? or longer?
    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.strptime(to_date, '%Y-%m-%d')
    current_date = from_date
    date_collections = []
    while current_date < to_date:
        until_date = current_date + timedelta(days=7)
        if until_date > to_date: until_date = to_date
        date_collections.append((current_date.strftime('%Y-%m-%d'), until_date.strftime('%Y-%m-%d')))
        current_date = until_date

    return date_collections

def create_user_folder(handle):
    """
        takes a name, creates a folder, returns a folder id
    """
    global root_folder_id
    if not root_folder_id: set_root_folder('twitter')

    data = {"name": handle}
    url = "%s/folders/%s/folders/?api_key=%s" % (PERMA_BASE_API, root_folder_id, PERMA_API_KEY)
    response = requests.post(url, json.dumps(data))
    return response.json()['id']

def create_perma_archive(archive_url, folder_id):
    url = "%s/archives/?api_key=%s" % (PERMA_BASE_API, PERMA_API_KEY)
    data = {"url": archive_url, "folder": folder_id}
    response = requests.post(url, json.dumps(data))

def create_perma_tweets(handles, from_date, to_date):
    # TODO: check when account was created
    ranges = create_weekly_ranges(from_date, to_date)

    for user in handles:
        folder_id = create_user_folder(user)
        for dates in ranges:
            to_encode = "from:%s since:%s until:%s" % (user, dates[0], dates[1])
            queries = "?q=%s&src=typd&lang=en" % urllib.quote(to_encode)
            url = TWITTER_BASE_URL + queries
            create_perma_archive(url, folder_id)

# TODO: def search_for_words(word, folder_name)
