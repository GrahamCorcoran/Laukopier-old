import praw
import config
import json
import time

ignored_subreddits = ["legaladvice",
                      "bestoflegaladvice",
                      "legaladviceofftopic"]


class load(object):
    """
    Reduces overhead in manipulating json file by handling the opening and dumping of data.
    """
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
    """
    Currently no function - possible future integration to handle context and comment threads.
    """
    pass


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
    :return: List of URL components, excluding underscores, empty elements, and queries.
    """
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


def post(reddit, thread, target_thread):
    """
    :param reddit: Reddit instance
    :param thread: /r/bestoflegaladvice thread object
    :param target_thread: thread object of whichever subreddit is being quoted.
    :action: Submits reply to thread.
    """
    testpost = reddit.submission("7usa17")

    title = target_thread.title
    body = target_thread.selftext

    body = body.split("\n\n")
    newbody = []

    # If body reduces spam by aborting when there is no selftext, for example when an image is posted.
    # Could possibly be handled instead by deliberately avoiding image posts, but this works for now.
    if body:

        # Adding quotes to each paragraph to match reddit formatting for quoting an entire post.
        for element in body:
            newbody.append("\n \n> " + element)
        body = "".join(newbody)
        header = "Title: " + title + "\n\n" + "Body: \n\n"
        footer = "\n\n This bot was created to capture threads missed by LocationBot." \
                 "\n\n [Concerns? Bugs?](https://www.reddit.com/message/compose/?to=laukopier)" \
                 " | [GitHub](https://github.com/Grambles/Laukopier)"

        # Compiles message for posting.
        formatted_message = header + body + footer

        # Submits post.
        thread.reply(formatted_message)


def work_thread(submission, reddit_instance):
    url = url_splitter(submission.url)

    # The subreddit name is always immediately following /r/ in a reddit URL.
    subreddit = url[url.index("r")+1].lower()
    if subreddit not in ignored_subreddits:
        target_thread = url[url.index("comments")+1]
        target_thread_obj = reddit_instance.submission(target_thread)
        title = target_thread_obj.title

        # This handles if a linked thread is a context or comment thread.
        if is_comment(target_thread, title, url):
            # Currently no post_comment_thread function is created, this instead passes.
            post_comment_thread(reddit_instance, title, target_thread_obj)
        else:
            try:
                # Replies to main thrad.
                post(reddit_instance, submission, target_thread_obj)
            except praw.exceptions.APIException:
                """
                This is currently handled poorly - it does not use a reasonable amount of time,
                and additionally it may crash if the bot were rate-limited twice in a row.
                This should be a high priority to resolve.
                """
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
                    """
                    Custom error URLError is caused when a link is posted from outside
                    of reddit, as it can not be parsed by PRAW.
                    """
                    pass


if __name__ == "__main__":
    main(login())
