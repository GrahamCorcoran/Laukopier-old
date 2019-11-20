import peewee

db = peewee.SqliteDatabase('laukopier.db')


class BaseModel(peewee.Model):

    class Meta:
        database = db


class BolaPost(BaseModel):

    reddit_id = peewee.CharField()
    url = peewee.CharField()
    is_self = peewee.BooleanField()
    created_utc = peewee.TimeField()


class Post(BaseModel):

    ignored_subreddits = ['legaladvice']

    reddit_id = peewee.CharField()
    author = peewee.CharField(null=True)
    created_utc = peewee.TimeField()
    edited = peewee.BooleanField()
    self_text = peewee.TextField()
    title = peewee.CharField()
    subreddit = peewee.CharField()

    @classmethod
    def insert_post(cls, post):
        if post.is_self:

            return Post.create(reddit_id=post.id,
                               author=post.author,
                               created_utc=post.created_utc,
                               edited=post.edited,
                               self_text=post.selftext,
                               title=post.title,
                               subreddit=post.subreddit)

    def format_message(self):
        # Adding quotes to each paragraph to match reddit formatting for quoting
        #  an entire post.

        body = self.self_text.split("\n\n")
        newbody = []

        for element in body:
            newbody.append("\n \n> " + element)

        body = "".join(newbody)
        header = "**Reminder:** Do not participate in threads linked here." \
                 " If you do, you may be banned from both subreddits." \
                 "\n\n --- \n\n" \
                 "Title: " + self.title + "\n\n" + "Body: \n\n"
        footer = "\n\n This bot was created to capture threads missed by LocationBot" \
                 " and is not affiliated with the mod team." \
                 "\n\n [Concerns? Bugs?](https://www.reddit.com/message/compose/?to=laukopier)" \
                 " | [GitHub](https://github.com/GrahamCorcoran/Laukopier)"

        # Compiles message for posting.
        formatted_message = header + body + footer

        return formatted_message


if __name__ == "__main__":
    if input("Are you trying to create a new database? Y/N: ").lower() in ["yes", "y"]:
        db.connect()
        db.create_tables([Post, BolaPost])