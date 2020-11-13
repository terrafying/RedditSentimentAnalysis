from psaw import PushshiftAPI
from datetime import datetime
from typing import List, Generator, NamedTuple
import json
# PRAW to interact with reddit
import praw

api = PushshiftAPI()

MAX_ITEMS = 100000

before = int(datetime(2020, 8, 1).timestamp())
after = int(datetime(2020, 9, 1).timestamp())

# Reddit API Wrapper
reddit = praw.Reddit(client_id='dwvhQN_PoUCoAw',
                     client_secret='X8N_SZUsiI-CNVIYLToBFFQ-cYE',
                     user_agent='news on hooks')

def gather_submissions(subreddit):
    submissions: List[NamedTuple] = list(
        api.search_submissions( after=after,
                                subreddit=subreddit,
                                limit=MAX_ITEMS)
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

def parse_psaw_to_list(l):
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
                yield comment.body
            else:
                continue
            replies_of(comment)

def top_posts_and_comments(subreddit):
    top_posts = reddit.subreddit(subreddit).top('week', limit=5)
    for submission in top_posts:
        submission_comm = reddit.submission(id=submission.id)

        for count, top_level_comment in enumerate(submission_comm.comments):
            for reply in replies_of(top_level_comment):
                yield reply

if __name__ == '__main__':
    sub = 'Cryptocurrency'
    with open(f'data/reddit/{sub}_submissions_{before}_{after}.json', 'w') as f:
        json.dump(gather_submissions(sub), f, indent=2)

    with open(f'data/reddit/{sub}_comments_{before}_{after}.json', 'w') as f:
        json.dump(gather_comments('Cryptocurrency'), f, indent=2)



