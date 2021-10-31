import tkinter as tk
from tkinter import filedialog
import os.path

class PathsWindow():
    def __init__(self, preferences, main_win):
        self.preferences = preferences
        self.main_win = main_win
        self.bg_color = 'AntiqueWhite2'
        self.btn_color = 'AntiqueWhite3'
        self.fg_color = 'black'
        self.font = ('Helvetica', 15)

        self.win = tk.Toplevel()
        self.win.title("Paths to files")
        self.win.geometry('900x260+600+200')
        self.win.config(bg=self.bg_color)
        self.win.grab_set() # Makes main window unusable until self.win closed

        # File list
        self.listbox_scrollbar = tk.Scrollbar(self.win, orient=tk.VERTICAL)
        self.file_listbox = tk.Listbox(self.win, width=60, height=5, bg=self.bg_color, fg=self.fg_color, font=self.font, yscrollcommand=self.listbox_scrollbar.set, activestyle='none')
        self.file_listbox.grid(column=0, row=0, padx=10, pady=(20,0))
        self.listbox_scrollbar.config(command=self.file_listbox.yview)
        self.listbox_scrollbar.grid(column=1, row=0, sticky=tk.NS)
        self.file_listbox.focus_set()

        # Add/Remove/Cancel/Save buttons (within a frame)
        self.button_frame = tk.Frame(self.win, bg=self.bg_color)
        self.button_frame.grid(row=3, column=0, columnspan=2, sticky='e')
        self.save_button = tk.Button(self.button_frame, text="Save", underline=0, bg=self.btn_color, state='disabled', font=self.font, command=lambda: self.save_changes(0))
        self.save_button.pack(side='right', padx=10, pady=20)
        self.cancel_button = tk.Button(self.button_frame, text="Cancel", underline=0, bg=self.btn_color, font=self.font, command=lambda: self.cancel_window(0))
        self.cancel_button.pack(side='left', padx=10, pady=20)
        self.remove_button = tk.Button(self.button_frame, text="Remove", underline=0, bg=self.btn_color, font=self.font, command=lambda: self.remove_path(0))
        self.remove_button.pack(side='right', padx=10, pady=20)
        self.add_button = tk.Button(self.button_frame, text="Add", underline=0, bg=self.btn_color, font=self.font, command=lambda: self.add_path(0))
        self.add_button.pack(side='right', padx=10, pady=20)

        # Keyboard shortcuts
        self.win.bind('p', self.cancel_window)
        self.win.bind('c', self.cancel_window)
        self.win.bind('<Escape>', self.cancel_window)
        self.win.bind('s', self.save_changes)
        self.win.bind('r', self.remove_path)
        self.win.bind('a', self.add_path)

        self.display_paths(False)


    def cancel_window(self, e):
        self.win.destroy()


    def display_paths(self, e):
        for d in self.preferences.dirs:
            self.file_listbox.insert('end', d)


    def add_path(self, e):
        new_path = filedialog.askdirectory()
        if new_path:
            self.file_listbox.insert('end', new_path)
            self.save_button['state'] = 'normal'


    def remove_path(self, e):
        self.file_listbox.delete(tk.ANCHOR)
        self.save_button['state'] = 'normal'


    def save_changes(self,e):
        new_dirs = self.file_listbox.get(0, 'end')
        self.preferences.dirs = new_dirs
        self.preferences.write_file()
        self.save_button['state'] = 'disabled'
        self.win.title("Your changes have been saved!")

        # Update the list of quizes in main menu:
        self.main_win.reset_file_list()
