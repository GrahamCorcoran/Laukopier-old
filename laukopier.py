import praw
import config
import json
import time

ignored_subreddits = ["legaladvice",
                      "bestoflegaladvice",
                      "legaladviceofftopic"]


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


def is_comment(thread, title, url):
    """
    Comment threads have two main indicators, all relating to the last element of the URL after it has
    queries and underscores removed.
    1) If the last element is the title with underscores instead of spaces (and on longer titles the
    title can be truncated), then it is not a comment thread.
    2) If the last element is just the target thread, then it is not a comment thread.
    Therefore if final_element is not the target thread identifier
    AND
    final_element is not part of the title
    then the thread is a comment.
    """
    final_element = url[-1].split("_")[0]
    return final_element != str(thread) and final_element not in title.lower()


def post_comment_thread(reddit_instance, title, submission_obj):
    print("Comment thread!")


def post_thread(reddit_instance, title, submission_obj):
    body = submission_obj.selftext
    print("Title: " + title)
    print("Body: " + body)
    reddit_instance.submission("7usa17").reply("Title: " + title + "\n \n" + "Body: \n \n > " + body)


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

    # Split's URL on slashes, breaking the URL into its components.
    split_url = url.split("/")

    # Removes underscores
    split_url = list(filter(lambda x: x != '_', split_url))

    # Removes empty values
    url_components = list(filter(None, split_url))

    # Removes last element where it's a query - not useful for parsing data.
    while '?' in url_components[-1]:
        url_components.pop()

    return url_components


def clear_json():
    with load(config.filename) as jsondata:
        print("Are you sure you want to clear all previously worked threads?")
        print("WARNING: THIS COULD POST TWICE ON THE SAME COMMENT, WHICH BREAKS REDDIT TOS")
        if input("Please type 'I understand.': ") == "I understand.":
            jsondata["ThreadID"] = []
            print("Threads reset.")
        else:
            print("Threads not reset.")


def post(reddit, thread, target_thread):
    testpost = reddit.submission("7usa17")

    title = target_thread.title
    body = target_thread.selftext
    body = body.split("\n\n")
    newbody = []

    for element in body:
        newbody.append("\n \n> " + element)
    body = "".join(newbody)
    header = "Title: " + title + "\n\n" + "Body: \n\n"
    footer = "\n\n This bot was created to capture threads missed by LocationBot." \
             "\n\n [Concerns? Bugs?](https://www.reddit.com/message/compose/?to=laukopier)" \
             " | [GitHub](https://github.com)"
    formatted_message = header + body + footer

    # WHEN READY TO DEPLOY, CHANGE testpost BELOW TO thread.
    testpost.reply(formatted_message)


def work_thread(submission, reddit_instance):
    url = url_splitter(submission.url)

    # The subreddit name is always immediately following /r/ in a reddit URL.
    subreddit = url[url.index("r")+1].lower()
    if subreddit not in ignored_subreddits:
        target_thread = url[url.index("comments")+1]
        target_thread_obj = reddit_instance.submission(target_thread)
        title = target_thread_obj.title

        if is_comment(target_thread, title, url):
            post_comment_thread(reddit_instance, title, target_thread_obj)
        else:
            try:
                post(reddit_instance, submission, target_thread_obj)
            except praw.exceptions.APIException:
                print("Sleeping per reddit request.")
                time.sleep(15)
                print("Waking up and trying again.")
                post(reddit_instance, submission, target_thread_obj)


def main(reddit_instance):
    bola = reddit_instance.subreddit("bestoflegaladvice")
    for submission in bola.stream.submissions():
        threadID = str(submission)

        with open(config.filename, 'r') as f:
            jsondata = json.load(f)
            # Checks to see if thread has already been worked. If it has, skips.
            if threadID not in jsondata["ThreadID"]:
                add_thread(str(submission))
                try:
                    work_thread(submission, reddit_instance)
                except URLError:
                    pass


if __name__ == "__main__":
    main(login())
