import os
import calendar
from tkinter import *
from tkinter import filedialog, messagebox
import matplotlib
from gather_data import ForumDataSource
from tkcalendar import DateEntry
from datetime import date, datetime
import re

from sentiment_analyzer import SentimentAnalyzer
from sentiment_intensity import plot_sentiment_intensity_in_frame, apply_sentiment_intensity

# global variables
matplotlib.use("TkAgg")
sub_name = ''

date_start = date.today()
date_end = date.today()

# regex for subreddit name validation
sub_name_pattern = re.compile('[a-zA-Z0-9_-]{3,21}')
global active_file


# class for popup window to enter subreddit name, store off to variable
class PopupWindow(object):

    def __init__(self, master):
        top = self.top = Toplevel(master)
        self.label = Label(top, text="Enter a Subreddit Name")
        self.label.pack()
        self.entry = Entry(top)
        self.entry.pack()
        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.pack()

    def cleanup(self):
        global sub_name
        if re.search(sub_name_pattern, self.entry.get()):
            sub_name = self.entry.get()
            self.top.destroy()
        else:
            messagebox.showerror("Error", "Invalid Subreddit name, try again")


# class for date selection popup window
class CalendarWindow(object):

    def __init__(self, master):
        self.before = int(datetime(2020, 9, 1).timestamp())
        self.after = int(datetime(2020, 8, 1).timestamp())

        top = self.top = Toplevel(root)
        self.label = Label(top, text='Choose date').pack(padx=10, pady=10)
        self.start_cal = DateEntry(top, width=12, background='darkblue',
                                   foreground='white', borderwidth=2)
        self.start_cal.pack(padx=10, pady=10)
        self.end_cal = DateEntry(top, width=12, background='darkblue',
                                 foreground='white', borderwidth=2)
        self.end_cal.pack(padx=10, pady=10)
        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.pack()

    # Function to deal with weird difference between date and datetime objects
    def cleanup(self):
        def to_epoch(d: datetime.date):
            return calendar.timegm(d.timetuple())

        # Set before and after attributes from calendar dates
        self.before = to_epoch(self.start_cal.get_date())
        self.after = to_epoch(self.end_cal.get_date())
        self.top.destroy()


# class for filebrowser to save file
# class FileBrowserSave(object):
#     def __init__(self, master):
#         global active_file
#         active_file = filedialog.asksaveasfilename(initialdir='/', title='Save Report as',
#                                                    filetypes=(("json gz files", "*.gz"), ("all files", "*.*")))
#
#
# # class for filebrowser to open file
# class FileBrowserOpen(object):
#     def __init__(self, master):
#         global active_file
#         active_file = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select File to Open',
#                                                  filetypes=(("json gz files", "*.gz"), ("all files", "*.*")))
#

# main gui window class
class MainWindow(object):

    def __init__(self, master):
        # set up GUI
        self.master = master
        master.geometry("600x400")
        master.title('Reddit Sentiment Analyzer')
        self.pane = PanedWindow(orient='horizontal')
        self.left_pane = PanedWindow(orient='vertical')
        self.right_pane = PanedWindow(orient='vertical')

        # code for GUI control buttons
        self.new_report_button = Button(text='New Report', width=15, height=1, command=self.calendar)
        self.new_report_button.pack(side=LEFT)
        self.left_pane.add(self.new_report_button)

        self.select_sub_button = Button(master, text='Select Subreddit', command=self.popup)
        self.select_sub_button.pack(side=LEFT)
        self.left_pane.add(self.select_sub_button)

        self.select_date_button = Button(master, text='Select Date', command=self.calendar, state=DISABLED)
        self.select_date_button.pack(side=LEFT)
        self.left_pane.add(self.select_date_button)

        self.collect_data_button = Button(master, text='Collect Data', width=15, height=1,
                                          command=self.collect_data, state=DISABLED)
        self.collect_data_button.pack(side=LEFT)
        self.left_pane.add(self.collect_data_button)

        self.build_report_button = Button(text='Build Report', width=15, height=1, command=self.build_report)
        self.build_report_button.pack(side=LEFT)
        self.left_pane.add(self.build_report_button)
        self.method_selection = StringVar()

        self.add_radio_button()

        # Dummy label to fix pane packing issues
        self.left_pane.add(Label(root, text=''))

        self.left_pane.pack(side=TOP, fill=NONE)

        # the right hand pane contains formatted data gathered from pushshift and analyzed by the analyzer
        # while left_pane is reserved for control button widgets

        self.pane.add(self.left_pane)
        self.pane.add(self.right_pane)

        self.pane.pack(fill=BOTH, expand=True, side=TOP)
        self.pane.configure(sashrelief=RAISED)

        self.data_source = ForumDataSource()
        # To contain extra windows
        self.popup_window = None
        self.w = None
        self.calendar = None

    def add_radio_button(self):
        label = Label(root,
                      text="""Sentiment analysis method""",
                      justify=LEFT,
                      padx=20)
        # label.pack()

        self.left_pane.add(label)
        # label.pack(side=TOP)

        R1 = Radiobutton(root, text="Quick", variable=self.method_selection, value='quick')
        # R1.pack(anchor=W, side=TOP)
        R1.select()

        self.left_pane.add(R1)

        R2 = Radiobutton(root, text="Accurate", variable=self.method_selection, value='accurate')
        # R2.pack(anchor=W, side=TOP)

        self.left_pane.add(R2)

        # self.left_pane.pack(side=TOP)

    # popup window to select daterange and subreddit to query, enables collect data when closed
    # if a subreddit name has been entered
    def popup(self):
        self.popup_window = PopupWindow(self.master)
        self.select_sub_button['state'] = 'disabled'
        self.master.wait_window(self.popup_window.top)
        self.select_sub_button['state'] = 'normal'
        self.select_date_button['state'] = 'normal'
        self.build_report_button['state'] = 'normal'

    # function for the collect data button
    def collect_data(self):
        # Gather sample data.  Just comments,.
        before = self.calendar.before
        after = self.calendar.after
        f_name = f'data/reddit/{sub_name}_comments_{before}_{after}.json.gz'
        self.data_source.gather_to_file(f_name, subreddit=sub_name, gather_type='comments')

    # def save_report(self):
    #     self.w = FileBrowserSave(self.master)
    #
    # def open_report(self):
    #     self.w = FileBrowserOpen(self.master)

    def build_report(self):
        global active_file
        global sub_name
        try:
            active_file = filedialog.askopenfilename(initialdir=os.getcwd(), title='Open Report',
                                                     filetypes=(("json gz files", "*.gz"), ("all files", "*.*")))
            print(active_file)
            sub_name = os.path.basename(active_file).split('_')[0]
            df = self.data_source.load_from_file(active_file)
            if self.method_selection.get() == 'quick':
                df = apply_sentiment_intensity(df)
            else:
                sentiment_analyzer = SentimentAnalyzer()
                df = sentiment_analyzer.predict(
                    df[::20])  # every Nth record - it is still too slow to process all records
            self.show_report(df)
        except FileNotFoundError as e:
            messagebox.showerror("Error",
                                 "Invalid file loaded. Please try gathering data again or selecting another dataset.")
            print(e)

    # Display report inside pane
    def show_report(self, df):
        canvas_frame = plot_sentiment_intensity_in_frame(df, self.master, sub_name)
        self.right_pane.add(canvas_frame)

    # calendar function - only enable data collection once a subreddit and a date have been chosen
    def calendar(self):
        self.calendar = CalendarWindow(self.master)
        self.select_date_button['state'] = 'disabled'
        self.master.wait_window(self.calendar.top)
        self.select_date_button['state'] = 'normal'
        self.collect_data_button['state'] = 'normal'


# instantiate GUI
if __name__ == "__main__":
    root = Tk()
    m = MainWindow(root)
    root.mainloop()
