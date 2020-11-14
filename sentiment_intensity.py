from datetime import datetime
from tkinter import Frame

import nltk
import pandas as pd
import matplotlib.pyplot as plt
# import seaborn as sns
# sns.set(style='darkgrid', context='talk', palette='Dark2')
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from nltk.corpus import stopwords

nltk.download('stopwords')
nltk.download('vader_lexicon')
stop_words = stopwords.words("english")
import gzip

# Shortest allowed comment (ignore comments shorter than X chars)
MINIMUM_COMMENT_LENGTH=20

# set up sentiment analyzer
sia = SIA()

def prepare_data(f_name, content_column='body') -> pd.DataFrame:
    df = pd.read_json(
        gzip.open(f_name, 'rt', encoding="utf-8"),
        encoding='utf-8'
    )

    # Drop non-useful items
    df.dropna(axis=0, subset=[content_column], inplace=True)
    df[content_column] = df[content_column].astype('str')
    # Use only text longer than 20 chars
    mask = (df[content_column].str.len() > MINIMUM_COMMENT_LENGTH)
    df = df.loc[mask]

    print(df.head(5))
    print(df.shape)

    # Parse UTC timestamp to date
    df['date'] = pd.to_datetime(df['created_utc'], unit='s', utc=True)

    return df


"""
Apply sentiment_method to dataframe
Return dataframe with results
"""
def apply_sentiment_intensity(df: pd.DataFrame,
                              content_column='body',
                              sentiment_method=sia.polarity_scores,
                              ax=None):
    # Expects sentiment_method to return a dictionary object
    x = pd.json_normalize(df[content_column].apply(sentiment_method))

    # Select relevant columns
    reduced_df: pd.DataFrame = df[['date']].join(x)
    reduced_df.set_index('date', inplace=True)

    return reduced_df

def plot_sentiment_intensity(df, master, sub_name):
    # the figure that will contain the plot
    fig = Figure(figsize=(5, 5),
                 dpi=100)

    # adding the subplot
    ax = fig.add_subplot(111)
    canvas_frame = Frame(master)
    # creating the Tkinter canvas
    # containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig,
                               master=canvas_frame)
    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().pack()

    df1 = apply_sentiment_intensity(
        df,
        content_column='body',
        ax=ax).ewm(span=100).mean()
    df1.plot(
        label='Moving average',
        cmap=plt.cm.rainbow,
        ax=ax)
    print('plotted')

    # creating the Matplotlib toolbar
    toolbar = NavigationToolbar2Tk(canvas,
                                   canvas_frame)
    toolbar.update()
    toolbar.pack_configure(expand=True)

    # placing the toolbar on the Tkinter window
    canvas.get_tk_widget().pack()

    return canvas_frame

import glob
from bert_sentiment import predict_sentiment

if __name__ == '__main__':
    sub = 'Monero'

    files = glob.glob(f'data/reddit/{sub}_comments*.gz')
    if len(files) < 1:
        print('No files found!')
        exit(1)
    for filename in files:
        df = prepare_data(filename)
        apply_sentiment_intensity(
            df,
            content_column='body').ewm(span=100).mean().plot(label='Moving average',
        cmap=plt.cm.rainbow)
        apply_sentiment_intensity(
            df[:100],
            content_column='body',
            sentiment_method=predict_sentiment,
        )