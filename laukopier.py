import settings
from models import BolaPost, Post
import praw
import prawcore
import time
import logging

logging.basicConfig(filename='laukopier.log')

while True:
    print("Laukopier started successfully.")
    try:

        r = praw.Reddit(username=settings.username,
                        password=settings.password,
                        client_id=settings.client_id,
                        client_secret=settings.secret,
                        user_agent=settings.user_agent)

        bola = r.subreddit('bestoflegaladvice')
        
        for submission in bola.stream.submissions(skip_existing=True):
            post = BolaPost.create(reddit_id=submission.id,
                                   created_utc=submission.created_utc,
                                   url=submission.url,
                                   is_self=submission.is_self)

            target = r.submission(url=post.url)
            target_data = Post.insert_post(target)
            if target_data and target_data.subreddit not in Post.ignored_subreddits:
                body = target_data.format_message()
                submission.reply(body)

    except prawcore.exceptions.ResponseException as e:
        if e.response.status_code in [429, 500, 502, 503, 504]:
            time.sleep(60)

    except Exception as e:
        logging.exception("Exception occurred")
        raise Exception

