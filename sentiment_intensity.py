import os

import matplotlib.pyplot as plt
import nltk
import pandas as pd
# import seaborn as sns
# sns.set(style='darkgrid', context='talk', palette='Dark2')
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from tkinter import Frame

from gather_data import ForumDataSource

nltk.download('stopwords')
nltk.download('vader_lexicon')
stop_words = stopwords.words("english")

# Shortest allowed comment (ignore comments shorter than X chars)
MINIMUM_COMMENT_LENGTH=20

# set up sentiment analyzer
sia = SIA()

def apply_sentiment_intensity(df: pd.DataFrame):
    """
    Apply SIA Polarity Score to dataframe
    :param df: Dataframe containing text to analyze
    :return: DataFrame indexed by date
    """
    # Map the (dict) results of SIA polarity scores onto our data
    x = pd.json_normalize(df.text.apply(sia.polarity_scores))

    # Add date column, index by date
    reduced_df: pd.DataFrame = df[['date']].join(x)
    reduced_df.set_index('date', inplace=True)

    return reduced_df


"""
Input: Reddit dataframe from the ForumDataSource
"""
def plot_sentiment_intensity(df, name=''):
    # df.index = pd.to_datetime(df.date)
    df.resample("H").mean().plot(title=f'Hourly mean score for {name}', cmap=plt.cm.rainbow)
    # Apply moving-window average, and plot results
    # df.ewm(span=100).mean().plot(
    #     label='Moving average',
    #     cmap=plt.cm.rainbow)



def plot_sentiment_intensity_in_frame(df, master, sub_name):
    """
    This is a method to display a PyPlot chart inside the GUI.

    Makes a pyplot inside a Frame

    Parameters
    ----------
    df: DataFrame containing sentiment intensity scores (from apply_sentiment_intensity).

    Returns
    --------
    A tkinter Frame containing the plot
    """
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

    # Apply moving-window average, and plot results
    df.resample("H").mean().plot(title=f'Hourly mean score for {sub_name}', ax=ax, cmap=plt.cm.rainbow)
    # df.ewm(span=100).mean().plot(
    #     label='Moving average',
    #     cmap=plt.cm.rainbow,
    #     ax=ax)

    print('Plotted moving average')

    # creating the Matplotlib toolbar
    toolbar = NavigationToolbar2Tk(canvas,
                                   canvas_frame)
    toolbar.update()
    toolbar.pack_configure(expand=True)

    # placing the toolbar on the Tkinter window
    canvas.get_tk_widget().pack()

    return canvas_frame

import glob

if __name__ == '__main__':
    # Monero subreddit comment data

    filenames = glob.glob('data/reddit/*_comments_*.json.gz')
    filename = filenames[0]

    data_source = ForumDataSource()
    df = data_source.load_from_file(filename)

    df = apply_sentiment_intensity(df)
    # df.index = pd.to_datetime(df.date)
    sub_name = os.path.basename(filename).split('_')[0]
    plot_sentiment_intensity(df.dropna(), name=sub_name)