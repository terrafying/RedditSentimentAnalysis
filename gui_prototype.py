from tkinter import *
from tkinter import filedialog

from tkcalendar import Calendar, DateEntry
import sys
from datetime import date

# global variables
sub_name = ''
date_start = date.today()
date_end = date.today()


# TODO: class containing json dump for stored report data, then feeding it into tkinter text widget as first step of
#  report view

# class for popup window to enter subreddit name, store off to variable
class PopupWindow(object):

    # TODO: add some level of validation to make sure there is a valid name entered
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
        sub_name = self.entry.get()
        self.top.destroy()


# class for date selection popup window
class CalendarWindow(object):

    # TODO: Make this a date range instead of single date
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
        top = self.top = Toplevel(root)
        file_to_save = filedialog.asksaveasfilename(initialdir='/', title='Save Report as',
                                                    filetypes=(("json files", "*.json"), ("all files", "*.*")))
        print(file_to_save)


# class for filebrowser to open file
# TODO: set this to read a saved json object
class FileBrowserOpen(object):
    def __init__(self, master):
        top = self.top = Toplevel(root)
        file_to_open = filedialog.askopenfilename(initialdir='/', title='Select File to Open',
                                                  filetypes=(("json files", "*.json"), ("all files", "*.*")))
        print(file_to_open)


# class for main GUI window
class MainWindow(object):
    # TODO: report build, load, save functionality
    # TODO: hook into gather_data, analyzer code
    def __init__(self, master):
        # set up GUI
        self.master = master
        master.geometry("500x300")
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
        self.build_report_button = Button(text='Build Report', width=15, height=1, state=DISABLED)
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

    # popup window to select daterange and subreddit to query, enables collect data when closed
    # if a subreddit name has been entered
    def popup(self):
        self.w = PopupWindow(self.master)
        self.select_sub_button['state'] = 'disabled'
        self.master.wait_window(self.w.top)
        self.select_sub_button['state'] = 'normal'
        self.select_date_button['state'] = 'normal'

    # function for the collect data button
    def collect_data(self):
        print(sub_name)
        print(date)

    def save_report(self):
        self.w = FileBrowserSave(self.master)

    def open_report(self):
        self.w = FileBrowserOpen(self.master)

    # calendar function - only enable data collection once a subreddit and a date have been chosen
    def calendar(self):
        self.w = CalendarWindow(self.master)
        self.select_date_button['state'] = 'disabled'
        self.master.wait_window(self.w.top)
        self.select_date_button['state'] = 'normal'
        self.collect_data_button['state'] = 'normal'


# TODO: finalize and clean this up
# instantiate GUI
if __name__ == "__main__":
    root = Tk()
    m = MainWindow(root)
    root.mainloop()
