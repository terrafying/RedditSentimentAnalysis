from datetime import datetime

import nltk
import pandas as pd
import math
import matplotlib.pyplot as plt
# import seaborn as sns
# sns.set(style='darkgrid', context='talk', palette='Dark2')
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('vader_lexicon')
stop_words = stopwords.words("english")
import gzip
import os

# set up sentiment analyzer
sia = SIA()

def vader_sentiment_intensity(f_name, content_column='body', group_by='day', sentiment_method=sia.polarity_scores):
    df = pd.read_json(
        gzip.open(f_name, 'rt', encoding="utf-8"),
        encoding='utf-8'
    )

    df.dropna(axis=0, subset=[content_column], inplace=True)

    print(df.head(5))
    print(df.shape)

    results = []

    # df = df[df[content_column] not in ("", "[removed]")]

    # analyze headlines
    for index, row in df.iterrows():
        pol_score = sentiment_method(row[content_column])
        df.loc[index, 'pol_score_pos'] = pol_score['pos']
        df.loc[index, 'pol_score_neg'] = pol_score['neg']
        # date = datetime.fromtimestamp(row['created_utc'])
        # df.loc[index, 'hour'] = int(date.hour)
        df.loc[index, 'block'] = int(row['created_utc'] / 500)
        pol_score[content_column] = row[content_column]
        results.append(pol_score)

    reduced_df: pd.DataFrame = df[['day', 'block', 'hour', content_column, 'pol_score_pos', 'pol_score_neg']]
    mean_df: pd.DataFrame = reduced_df.groupby([group_by]).mean(['pol_score_pos', 'pol_score_neg'])
    mean_df = mean_df.reset_index()
    # mean_df = reduced_df.resample(group_by, how='mean')

    print(mean_df.columns)
    print(mean_df.shape)
    print(mean_df.head(5))

    # mean_df.plot()
    # TODO: Display x-axis by time.  See: https://stackoverflow.com/questions/4090383/plotting-unix-timestamps-in-matplotlib
    plt.plot('pol_score_pos', data=mean_df, marker='', color='green', linewidth=2)
    plt.plot('pol_score_neg', data=mean_df, marker='', color='red', linewidth=2)
    plt.xlabel(group_by)
    # plt.ylabel('score')
    plt.legend()
    plt.show()

    # beautify the x-labels
    # plt.gcf().autofmt_xdate()
    print('max score')
    max_row: pd.DataFrame = reduced_df[reduced_df.pol_score_pos == df.pol_score_pos.max()]
    print(
        max_row[[content_column]]
    )
    print(max_row.values[0])


if __name__ == '__main__':
    vader_sentiment_intensity(f_name='data/reddit/Cryptocurrency_comments_1598932800_1596254400.json.gz',
                              content_column='body',
                              group_by='day')