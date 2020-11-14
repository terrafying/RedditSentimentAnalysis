import os
from tkinter import *
from tkinter import filedialog, messagebox
import matplotlib
import gather_data
from tkcalendar import DateEntry
from datetime import date
import re
from sentiment_intensity import prepare_data, plot_sentiment_intensity

# global variables
matplotlib.use("TkAgg")
sub_name = ''
date_start = date.today()
date_end = date.today()

# regex for subreddit name validation
sub_name_pattern = re.compile('[a-zA-Z0-9_-]{3,21}')


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
        top = self.top = Toplevel(root)
        self.l = Label(top, text='Choose date').pack(padx=10, pady=10)
        self.start_cal = DateEntry(top, width=12, background='darkblue',
                                   foreground='white', borderwidth=2)
        self.start_cal.pack(padx=10, pady=10)
        self.end_cal = DateEntry(top, width=12, background='darkblue',
                                 foreground='white', borderwidth=2)
        self.end_cal.pack(padx=10, pady=10)
        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.pack()

    def cleanup(self):
        global date_start
        global date_end
        date_start = self.start_cal.get_date()
        date_end = self.end_cal.get_date()
        self.top.destroy()


# class for filebrowser to save file
# TODO: set this to write json object returned from pushshift to file_to_save
class FileBrowserSave(object):
    def __init__(self, master):
        # top = self.top = Toplevel(root)
        file_to_save = filedialog.asksaveasfilename(initialdir='/', title='Save Report as',
                                                    filetypes=(("json files", "*.json"), ("all files", "*.*")))
        print(file_to_save)


# class for filebrowser to open file
# TODO: set this to read a saved json object
class FileBrowserOpen(object):
    def __init__(self, master):
        # top = self.top = Toplevel(root)
        file_to_open = filedialog.askopenfilename(initialdir=os.getcwd(), title='Select File to Open',
                                                  filetypes=(("json files", "*.json"), ("all files", "*.*")))
        print(file_to_open)


# class for main GUI window
class MainWindow(object):
    # TODO: report build, load, save functionality
    # TODO: hook into gather_data, analyzer code
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

        self.build_report_button = Button(text='Build Report', width=15, height=1, command=self.build_report,
                                          state=DISABLED)
        self.build_report_button.pack(side=LEFT)
        self.left_pane.add(self.build_report_button)

        self.save_report_button = Button(text='Save Report', width=15, height=1, command=self.save_report,
                                         state=DISABLED)
        self.save_report_button.pack(side=LEFT)
        self.left_pane.add(self.save_report_button)
        self.load_report_button = Button(text='Load Report', height=1, width=15, command=self.open_report)
        self.load_report_button.pack(side=LEFT)
        self.left_pane.add(self.load_report_button)

        # the right hand pane will contain the formatted data gathered from pushshift and analyzed by the analyzer
        # note that the label here is a placeholder for the actual widgets that will go inside of right_pane
        # while left_pane is reserved for control button widgets
        self.place_holder_label = Label(text='Placeholder for Report')
        self.place_holder_label.pack(side=RIGHT)
        self.right_pane.add(self.place_holder_label)
        self.pane.add(self.left_pane)
        self.pane.add(self.right_pane)
        self.pane.pack(fill=BOTH, expand=True)
        self.pane.configure(sashrelief=RAISED)

        # To contain extra windows
        self.popup_window = None
        self.w = None

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
        gather_data.gather(sub_name)
        print(sub_name)
        print(date)

    def save_report(self):
        self.w = FileBrowserSave(self.master)

    def open_report(self):
        self.w = FileBrowserOpen(self.master)

    def build_report(self):
        self.show_report()
        pass

    # Display report inside pane
    def show_report(self):
        df = prepare_data('data/reddit/Monero_comments_1598932800_1596254400.json.gz')
        print(df)
        canvas_frame = plot_sentiment_intensity(df, self.master, sub_name=sub_name)
        self.right_pane.add(canvas_frame)

    # calendar function - only enable data collection once a subreddit and a date have been chosen
    def calendar(self):
        self.w = CalendarWindow(self.master)
        self.select_date_button['state'] = 'disabled'
        self.master.wait_window(self.w.top)
        self.select_date_button['state'] = 'normal'
        self.collect_data_button['state'] = 'normal'


# instantiate GUI
if __name__ == "__main__":
    root = Tk()
    m = MainWindow(root)
    root.mainloop()
