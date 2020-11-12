import nltk
import pandas as pd
import math
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='darkgrid', context='talk', palette='Dark2')
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('vader_lexicon')
stop_words = stopwords.words("english")
import gzip
import os

def vader_sentiment_intensity(f_name, content_column='body'):
    df = pd.read_json(
        gzip.open(f_name, 'rt', encoding="utf-8"),
        encoding='utf-8'
    )

    df.dropna(axis=0, subset=[content_column], inplace=True)

    print(df[[content_column, 'created']][:5])

    # set up sentiment analyzer
    sia = SIA()
    results = []

    GROUP_BY = 'hour'

    # analyze headlines
    for index, row in df.iterrows():
        if row[content_column] in ("", "[removed]"):
            continue
        pol_score = sia.polarity_scores(row[content_column])
        df.loc[index, 'pol_score_pos'] = pol_score['pos']
        df.loc[index, 'pol_score_neg'] = pol_score['neg']
        df.loc[index, 'block'] = int(row['created_utc'] / 100)
        pol_score[content_column] = row[content_column]
        results.append(pol_score)

    # grouped_df['block'] = grouped_df.apply(lambda x: int(x / 100))
    reduced_df: pd.DataFrame = df[['block', 'hour', 'created_utc', content_column, 'pol_score_pos', 'pol_score_neg']]
    min_df: pd.DataFrame = reduced_df.groupby([GROUP_BY]).mean(['pol_score_pos', 'pol_score_neg'])
    print(min_df[:1])
    print(list(min_df.head().index))
    # make up some data
    x = range(len(min_df))
    y = min_df['pol_score_pos'] - min_df['pol_score_neg']
    # plot
    plt.plot(x, y)
    plt.xlabel(GROUP_BY)
    plt.ylabel('score')
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
    vader_sentiment_intensity(f_name='data/reddit/Cryptocurrency_comments_1598932800_1596254400.json.gz', content_column='body')