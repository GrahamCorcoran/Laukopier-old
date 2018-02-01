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


class URLError(Exception):
    pass


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


def url_splitter(url):
    """
    :param url: Reddit URL
    :return: Subreddit as string
             Target post as string
             Comment_thread as a boolean: True if comment thread
    """
    print(url)
    if "reddit" not in url:
        raise URLError("URL passed into function not from reddit.")

    split_url = url.split("/")
    # Removes underscores
    removed_underscores = list(filter(lambda x: x != '_', split_url))
    # Removes empty values
    url_components = list(filter(None, removed_underscores))
    # Removes last element where it's a query - not useful for parsing data.
    while '?' in url_components[-1]:
        url_components.pop()

    return url_components
    """
    ---
    Outdated URL Splitter code below
    ---
    comment_thread = False
    subreddit = url_components[url_components.index("r")+1]
    target_submission = url_components[url_components.index("comments")+1]
    last_element = url_components[-1].split("_")

    if last_element[0] != target_submission and len(last_element) == 1:
        comment_thread = True

    return subreddit, target_submission, comment_thread
    """

def clear_json():
    with load(config.filename) as jsondata:
        print("Are you sure you want to clear all previously worked threads?")
        print("WARNING: THIS COULD POST TWICE ON THE SAME COMMENT, WHICH BREAKS REDDIT TOS")
        if input("Please type 'I understand.': ") == "I understand.":
            jsondata["ThreadID"] = []
            print("Threads reset.")
        else:
            print("Threads not reset.")


def work_thread(submission, reddit_instance):
    url = url_splitter(submission.url)

    # The subreddit name is always immediately following /r/ in a reddit URL.
    subreddit = url[url.index("r")+1].lower()
    if subreddit == "legaladvice" or subreddit == "bestoflegaladvice":
        print("Skipping legaladvice thread -- handled by LocationBot.")
    else:
        target_thread = url[url.index("comments")+1]
        target_thread_obj = reddit_instance.submission(target_thread)
        title = target_thread_obj.title
        final_elements = [title.split()[0].lower(),
                          target_thread]
        print(final_elements)

        print(subreddit, target_thread)
        print(url)


def main(reddit_instance):
    bola = reddit_instance.subreddit("bestoflegaladvice")
    for submission in bola.stream.submissions():
        threadID = str(submission)

        with open(config.filename, 'r') as f:
            jsondata = json.load(f)
            # Checks to see if thread has already been worked. If it has, skips.
            if threadID in jsondata["ThreadID"]:
                pass
            else:
                add_thread(str(submission))
                try:
                    work_thread(submission, reddit_instance)
                except URLError:
                    pass

clear_json()
if __name__ == "__main__":
    main(login())
