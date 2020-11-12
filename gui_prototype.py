from tkinter import *
from tkcalendar import Calendar, DateEntry
import sys


# class for popup window to enter subreddit name, store off to variable
class PopupWindow(object):

    def __init__(self, master):
        global sub_name
        top = self.top = Toplevel(master)
        self.l = Label(top, text="Enter a Subreddit Name")
        self.l.pack()
        self.e = Entry(top)
        self.e.pack()
        sub_name = self.e.get()
        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.pack()

    def cleanup(self):
        self.value = self.e.get()
        sub_name = self.value
        self.top.destroy()


# class for main GUI window
class MainWindow(object):
    def __init__(self, master):
        self.master = master
        master.geometry("500x300")
        master.title('Reddit Sentiment Analyzer')
        self.pane = PanedWindow(orient='horizontal')
        self.left_pane = PanedWindow(orient='vertical')
        self.right_pane = PanedWindow(orient='vertical')
        self.select_sub_button = Button(master, text='Select Subreddit', command=self.popup)
        self.select_sub_button.pack(side=LEFT)
        self.left_pane.add(self.select_sub_button)
        self.collect_data_button = Button(master, text='Collect Data',
                                          command=lambda: sys.stdout.write(self.entryValue() + '\n'), state=DISABLED, )
        self.collect_data_button.pack(side=LEFT)
        self.left_pane.add(self.collect_data_button)
        self.build_report_button = Button(text='Build Report', width=15, height=1, state=DISABLED, )
        self.build_report_button.pack(side=LEFT)
        self.left_pane.add(self.build_report_button)
        self.save_report_button = Button(text='Save Report', width=15, height=1, state=DISABLED, )
        self.save_report_button.pack(side=LEFT)
        self.left_pane.add(self.save_report_button)
        self.load_report_button = Button(text='Load Report', width=15, height=1, state=DISABLED, )
        self.load_report_button.pack(side=LEFT)
        self.left_pane.add(self.load_report_button)
        self.new_report_button = Button(text='New Report', width=15, height=1, command=self.calendar)
        self.new_report_button.pack(side=LEFT)
        self.left_pane.add(self.new_report_button)
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
        self.collect_data_button['state'] = 'normal'

    def calendar(self):
        top = Toplevel(root)
        Label(top, text='Choose date').pack(padx=10, pady=10)
        self.cal = DateEntry(top, width=12, background='darkblue',
                             foreground='white', borderwidth=2)
        self.cal.pack(padx=10, pady=10)

    def entryValue(self):
        return self.w.value


if __name__ == "__main__":
    root = Tk()
    m = MainWindow(root)
    root.mainloop()
