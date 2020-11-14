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

with open('credentials.json') as creds_file:
    params = json.load(creds_file)

reddit = praw.Reddit(client_id=params['client_id'],
                     client_secret=params['api_key'],
                     user_agent='Sentiment Analyzer')

def gather(subreddit: str, gather_type='comments') -> Generator:
    if gather_type == 'comments':
        gen: Generator[NamedTuple, None, None] = api.search_comments(
            subreddit='Cryptocurrency',
            before=before,
            after=after,
            limit=MAX_ITEMS)
    else:
        gen: Generator[NamedTuple, None, None] = api.search_submissions(
                                    before=before,
                                    after=after,
                                    subreddit=subreddit,
                                    limit=MAX_ITEMS
                                    )
    return parse_pushshift_data(gen)

"""
Input: Generator from Pushshift api wrapper (result of api.search query)
Output: Yields dictionary items
"""
def parse_pushshift_data(l: Generator, type='comments') -> Generator[dict, None, None]:
    # Pushshift api wrapper returns objects with attribute "d_" containing dict
    for c in l:
        date = datetime.fromtimestamp(c.d_['created'])
        date_dict = {'day': date.day, 'month': date.month, 'hour': date.hour}
        content_field = 'body' if type=='comments' else 'selftext'
        yield {**c.d_, **date_dict,
               'content': c.d_[content_field]
               }

# Enumerate replies on a comment
def replies_of(top_level_comment: praw.reddit.Comment) -> Generator[praw.reddit.Comment, None, None]:
    if len(top_level_comment.replies) == 0:
        return
    else:
        for num, comment in enumerate(top_level_comment.replies):
            if comment.body:
                yield comment
            else:
                continue
            yield replies_of(comment)

def top_posts_and_comments(subreddit: str):
    top_posts = reddit.subreddit(subreddit).top('week', limit=50)
    for submission in top_posts:
        submission_comm = reddit.submission(id=submission.id)

        for count, top_level_comment in enumerate(submission_comm.comments):
            for reply in replies_of(top_level_comment):
                yield reply

def gather_to_file(f_name):
    if os.path.exists(f_name):
        # Todo: put this message in the GUI?
        print('file already exists')
    else:
        with gzip.open(f_name, 'wt', encoding="utf-8") as zipfile:
            l = list(gather(sub, gather_type=_gather_type))
            if len(l) < 2:
                print('Result is really short! Not saving.')
                print(l)
            else:
                json.dump(l, zipfile, indent=2)
    pass

if __name__ == '__main__':
    sub = 'Monero'

    # Gather sample data
    for _gather_type in ['submissions', 'comments']:
        f_name = f'data/reddit/{sub}_{_gather_type}_{before}_{after}.json.gz'
        if not os.path.exists(f_name):
            with gzip.open(f_name, 'wt', encoding="utf-8") as zipfile:
                l = list(gather(sub, gather_type=_gather_type))
                if len(l) < 2:
                    print('Result is really short! Not saving.')
                    print(l)
                else:
                    json.dump(l, zipfile, indent=2)




