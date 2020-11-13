from psaw import PushshiftAPI
from datetime import datetime
from typing import List, Generator, NamedTuple
import json
import gzip
# PRAW to interact with reddit
import praw
import os

api = PushshiftAPI()

MAX_ITEMS = 100000

before = int(datetime(2020, 9, 1).timestamp())
after  = int(datetime(2020, 8, 1).timestamp())

# Reddit API Wrapper
reddit = praw.Reddit(client_id='dwvhQN_PoUCoAw',
                     client_secret='X8N_SZUsiI-CNVIYLToBFFQ-cYE',
                     user_agent='news on hooks')

def gather_submissions(subreddit):
    submissions: Generator[NamedTuple] = api.search_submissions(
                                before=before,
                                after=after,
                                subreddit=subreddit,
                                )

    return parse_psaw_to_list(submissions)

def gather_comments(subreddit):
    # Comment search API
    # Can also take 'q' parameter for search query
    gen: Generator[NamedTuple, None, None] = api.search_comments(
        subreddit='Cryptocurrency',
        after=after,
        limit=MAX_ITEMS)
    return parse_psaw_to_list(gen)

def parse_psaw_to_list(l: Generator):
    # Pushshift api wrapper returns objects with attribute "d_" containing dict
    for c in l:
        date = datetime.fromtimestamp(c.d_['created'])
        yield {**c.d_, 'day': date.day, 'month': date.month, 'hour': date.hour}

# Enumerate replies on a comment
def replies_of(_top_level_comment):
    if len(_top_level_comment.replies) == 0:
        return
    else:
        for num, comment in enumerate(_top_level_comment.replies):
            if comment.body:
                yield comment
            else:
                continue
            yield replies_of(comment)

def top_posts_and_comments(subreddit):
    top_posts = reddit.subreddit(subreddit).top('week', limit=5)
    for submission in top_posts:
        submission_comm = reddit.submission(id=submission.id)

        for count, top_level_comment in enumerate(submission_comm.comments):
            for reply in replies_of(top_level_comment):
                yield reply

if __name__ == '__main__':
    sub = 'Cryptocurrency'


    f_name = f'data/reddit/{sub}_submissions_{before}_{after}.json.gz'
    if not os.path.exists(f_name):
        with gzip.open(f_name, 'wt', encoding="utf-8") as zipfile:
            json.dump(list(gather_submissions(sub)), zipfile, indent=2)

    f_name = f'data/reddit/{sub}_comments_{before}_{after}.json.gz'
    if not os.path.exists(f_name):
        with gzip.open(f_name, 'wt', encoding="utf-8") as zipfile:
            json.dump(list(gather_comments(sub)), zipfile, indent=2)





