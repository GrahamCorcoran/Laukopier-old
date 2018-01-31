import praw
import config
import json


class load(object):
    def __init__(self, filename):
        self.filename = filename

        with open(self.filename, 'r') as f:
            self.data = json.load(f)

    def __enter__(self):
        return self.data

    def __exit__(self, type, value, tb):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)


def login():
    """
    Returns a reddit instance using your bot login information in config.py
    Usage example: r = login()
    """
    return praw.Reddit(username=config.username,
                       password=config.password,
                       client_id=config.client_id,
                       client_secret=config.client_secret,
                       user_agent=config.user_agent)


def add_thread(thread):
    """
    Takes a submissionID and adds it to filename (set in config).
    """
    with load(config.filename) as subreddit_data:
        if thread not in subreddit_data["ThreadID"]:
            subreddit_data["ThreadID"].append(thread)


def subreddit_finder(url):
    """
    Takes a reddit.com URL and returns the subreddit that URL is from.
    """
    for index, char in enumerate(url):
        if url[index-3:index] == "/r/":
            testindex = index+1
            while url[testindex] != '/':
                testindex += 1
            return url[index:testindex]


def main(reddit_instance):
    bola = reddit_instance.subreddit("bestoflegalasdvice")
    for submission in bola.stream.submissions():
        add_thread(str(submission))
        print(subreddit_finder(submission.url))


if __name__ == "__main__":
    main(login())