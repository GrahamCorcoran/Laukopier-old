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
    Takes a submissionID and adds it to list of completed threads (set in config).
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


def clear_json():
    with load(config.filename) as jsondata:
        print("Are you sure you want to clear all previously worked threads?")
        print("WARNING: THIS COULD POST TWICE ON THE SAME COMMENT, WHICH BREAKS REDDIT TOS")
        if input("Please type 'I understand.': ") == "I understand.":
            jsondata["ThreadID"] = []
            print("Threads reset.")
        else:
            print("Threads not reset.")


def main_thread(url):
    print("This is a main thread.")
    print(url)
    print("---")


def context_thread(url):
    print("This is a context thread.")
    print(url)
    print("---")


def work_thread(submission):
    # Determines whether thread is a self post or referencing a comment, handles appropriately.
    url = submission.url
    if 'context' in url:
        context_thread(url)
    else:
        main_thread(url)


def main(reddit_instance):
    bola = reddit_instance.subreddit("bestoflegaladvice")
    for submission in bola.stream.submissions():
        threadID = str(submission)
        subreddit = subreddit_finder(submission.url).lower()

        with open(config.filename, 'r') as f:
            jsondata = json.load(f)
            # Checks to see if thread has already been worked. If it has, skips.
            if threadID in jsondata["ThreadID"]:
                pass
            else:
                add_thread(str(submission))
                if subreddit == "legaladvice" or subreddit == "bestoflegaladvice":
                    pass
                else:
                    work_thread(submission)


clear_json()
if __name__ == "__main__":
    main(login())
