from tkinter import *
from tkcalendar import Calendar, DateEntry
import sys
from datetime import date

sub_name = ''
date = date.today()

# class for popup window to enter subreddit name, store off to variable
class PopupWindow(object):

    def __init__(self, master):
        top = self.top = Toplevel(master)
        self.l = Label(top, text="Enter a Subreddit Name")
        self.l.pack()
        self.e = Entry(top)
        self.e.pack()
        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.pack()

    def cleanup(self):
        global sub_name
        sub_name = self.e.get()
        self.top.destroy()


# class for date selection popup window
class CalendarWindow(object):

    def __init__(self, master):
        top = self.top = Toplevel(root)
        self.l = Label(top, text='Choose date').pack(padx=10, pady=10)
        self.cal = DateEntry(top, width=12, background='darkblue',
                             foreground='white', borderwidth=2)
        self.cal.pack(padx=10, pady=10)
        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.pack()

    def cleanup(self):
        global date
        date = self.cal.get_date()
        self.top.destroy()


# class for main GUI window
class MainWindow(object):
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
                                          command=self.collect_data, state=DISABLED, )
        self.collect_data_button.pack(side=LEFT)
        self.left_pane.add(self.collect_data_button)
        self.build_report_button = Button(text='Build Report', width=15, height=1, state=DISABLED, )
        self.build_report_button.pack(side=LEFT)
        self.left_pane.add(self.build_report_button)
        self.save_report_button = Button(text='Save Report', width=15, height=1, state=DISABLED, )
        self.save_report_button.pack(side=LEFT)
        self.left_pane.add(self.save_report_button)
        self.load_report_button = Button(text='Load Report', width=15, height=1, )
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
        self.collect_data_button['state'] = 'normal'

    # function for the collect data button
    def collect_data(self):
        print(sub_name)
        print(date)

    # calendar function
    def calendar(self):
        self.w = CalendarWindow(self.master)
        self.select_date_button['state'] = 'disabled'
        self.master.wait_window(self.w.top)
        self.select_date_button['state'] = 'normal'


# instantiate GUI
if __name__ == "__main__":
    root = Tk()
    m = MainWindow(root)
    root.mainloop()
