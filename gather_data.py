from psaw import PushshiftAPI
from datetime import datetime
from typing import List, Generator, NamedTuple
import json
import gzip
import pandas as pd
# PRAW to interact with reddit
import praw
import os

api = PushshiftAPI()

MAX_ITEMS = 100000

before = int(datetime(2020, 9, 1).timestamp())
after  = int(datetime(2020, 8, 1).timestamp())

class ForumDataSource(object):
    """

    """
    def __init__(self):
        with open('credentials.json') as creds_file:
            params = json.load(creds_file)
        self.reddit = praw.Reddit(client_id=params['client_id'],
                     client_secret=params['api_key'],
                     user_agent='Sentiment Analyzer')


    def gather(self, subreddit: str, gather_type='comments') -> Generator:
        """
        Input
        -----
        Subreddit name, and gather_type (either 'comments' or 'submissions')

        Output
        ------
        Generator object, which yields a NamedTuple containing information about a submission or comment
        """
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
        return self.parse_pushshift_data(gen)

    """
    Input: Generator from Pushshift api wrapper (result of api.search query)
    Output: Yields dictionary items
    """
    def parse_pushshift_data(self, l: Generator, type='comments') -> Generator[dict, None, None]:
        # Pushshift api wrapper returns objects with attribute "d_" containing dict
        for c in l:
            date = datetime.fromtimestamp(c.d_['created'])
            date_dict = {'day': date.day, 'month': date.month, 'hour': date.hour}
            content_field = 'body' if type=='comments' else 'selftext'
            yield {**c.d_, **date_dict,
                   'content': c.d_[content_field]
                   }

    # Enumerate replies on a comment
    def replies_of(self, top_level_comment: praw.reddit.Comment) -> Generator[praw.reddit.Comment, None, None]:
        if len(top_level_comment.replies) == 0:
            return
        else:
            for num, comment in enumerate(top_level_comment.replies):
                if comment.body:
                    yield comment
                else:
                    continue
                yield self.replies_of(comment)

    def top_posts_and_comments(self, subreddit: str):
        top_posts = self.reddit.subreddit(subreddit).top('week', limit=50)
        for submission in top_posts:
            submission_comm = self.reddit.submission(id=submission.id)

            for count, top_level_comment in enumerate(submission_comm.comments):
                for reply in self.replies_of(top_level_comment):
                    yield reply

    def gather_to_file(self, filename, subreddit='Monero', gather_type='comments'):
        """
            Gather data from pushshift API (using self.gather()) and record the results to file

            :param filename: Where to save results
            :param subreddit: Subreddit to scrape
            :param gather_type: comments or submissions
        """
        if os.path.exists(filename):
            # Todo: put this message in the GUI?
            print('file already exists')
        else:
            with gzip.open(filename, 'wt', encoding="utf-8") as zipfile:
                l = list(self.gather(subreddit, gather_type=gather_type))
                if len(l) < 2:
                    print('Result is really short! Not saving.')
                    print(l)
                else:
                    json.dump(l, zipfile, indent=2)

    def load_from_file(self, filename, content_column='body') -> pd.DataFrame:
        """
        Build a DataFrame from the saved JSON.

        Input: filename of gzipped JSON
        """
        df: pd.DataFrame = pd.read_json(
            gzip.open(filename, 'rt', encoding="utf-8"),
            encoding='utf-8'
        )

        # Drop empty items
        df.dropna(axis=0, subset=[content_column], inplace=True)
        df[content_column] = df[content_column].astype('str')
        # Use only text longer than 20 chars
        df = df.loc[df[content_column].str.len() > 20]

        print(f'preparing data from {filename}')

        # Parse UTC timestamp to date
        df['date'] = pd.to_datetime(df['created_utc'], unit='s', utc=True)
        # Index by date
        # df.set_index('date', inplace=True)

        # Standardize text column to 'text'
        df.rename(columns={content_column: 'text'}, inplace=True)

        # columns = ['score','id','date','author','text']

        return df

if __name__ == '__main__':
    subreddit = 'Monero'

    data_source = ForumDataSource()

    # Gather sample data
    for gather_type in ['submissions', 'comments']:
        f_name = f'data/reddit/{subreddit}_{gather_type}_{before}_{after}.json.gz'
        data_source.gather_to_file(f_name, subreddit=subreddit, gather_type=gather_type)




