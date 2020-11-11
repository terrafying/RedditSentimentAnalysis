from tkinter import *
from tkcalendar import Calendar, DateEntry
import sys


# class for popup window to enter subreddit
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
        self.value = self.e.get()
        self.top.destroy()


# class for main GUI window
class MainWindow(object):
    def __init__(self, master):
        self.master = master
        master.geometry("500x200")
        master.title('Reddit Sentiment Analyzer')
        self.select_sub_button = Button(master, text='Select Subreddit', command=self.popup)
        self.select_sub_button.pack()
        self.collect_data_button = Button(master, text='Collect Data',
                                          command=lambda: sys.stdout.write(self.entryValue() + '\n'), state=DISABLED, )
        self.collect_data_button.pack()
        self.build_report_button = Button(text='Build Report', width=15, height=1, state=DISABLED, )
        self.build_report_button.pack()
        self.save_report_button = Button(text='Save Report', width=15, height=1, state=DISABLED, )
        self.save_report_button.pack()
        self.load_report_button = Button(text='Load Report', width=15, height=1, state=DISABLED, )
        self.load_report_button.pack()
        self.new_report_button = Button(text='New Report', width=15, height=1, command=self.calendar )
        self.new_report_button.pack()

    def popup(self):
        self.w = PopupWindow(self.master)
        self.select_sub_button['state'] = 'disabled'
        self.master.wait_window(self.w.top)
        self.select_sub_button['state'] = 'normal'

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
