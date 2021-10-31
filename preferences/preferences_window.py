import tkinter as tk
from tkinter import ttk


class PreferencesWindow:
    def __init__(self, preferences):
        self.preferences = preferences
        self.win = tk.Toplevel()
        self.win.title("Preferences")
        self.width = self.win.winfo_screenwidth()
        self.height = self.win.winfo_screenheight()
        self.x, self.y = (self.width // 2) -250, (self.height - 700) // 3
        self.win.geometry(f'+{self.x}+{self.y}')
        self.bg_color = 'AntiqueWhite2'
        self.btn_color = 'AntiqueWhite3'
        self.fg_color = 'black'
        self.font = ('Helvetica', 15)

        self.win.config(bg=self.bg_color)
        self.win.focus_set()
        self.win.grab_set() # Makes main window unusable until self.win closed

        # Label: Saving Preferences:
        Save_title_label = tk.Label(self.win, text="Saving Preferences:", font=self.font, bg=self.bg_color, fg=self.fg_color)
        Save_title_label.grid(row=5, column=0, padx=10, pady=10, sticky='w')

        # Choose to randomize questions or not:
        order_label = tk.Label(self.win, text="Randomize Questions:", font=self.font, bg=self.bg_color, fg=self.fg_color)
        order_label.grid(row=0, column=0, padx=10, pady=(30,10), sticky='w')
        self.order_var = tk.StringVar()
        self.order_dropdown = self.dropdown(self.order_var, 'Ordered', 'Random', self.preferences.random)
        self.order_dropdown.grid(row=0, column=1, padx=10, pady=(30,10), sticky='w')

        # Choose to have questions or answers shown first
        answer_first_label = tk.Label(self.win, text="Show First:", font=self.font, bg=self.bg_color, fg=self.fg_color)
        answer_first_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.answer_first_var = tk.StringVar()
        self.answer_first_dropdown = self.dropdown(self.answer_first_var, 'Questions', 'Answers', self.preferences.reversed)
        self.answer_first_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky='w')

        # Choose to have the counter on or off
        counter_label = tk.Label(self.win, text="Counter:", font=self.font, bg=self.bg_color, fg=self.fg_color)
        counter_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.counter_var = tk.StringVar()
        self.counter_dropdown = self.dropdown(self.counter_var, 'Enable', 'Disable', self.preferences.counter_off)
        self.counter_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky='w')

        # Single or dual mode
        display_a_label = tk.Label(self.win, text="Display Answers:", font=self.font, bg=self.bg_color, fg=self.fg_color)
        display_a_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.display_a_var = tk.StringVar()
        self.display_a_dropdown = self.dropdown(self.display_a_var, 'Dual', 'Single', self.preferences.single_mode)
        self.display_a_dropdown.grid(row=3, column=1, padx=10, pady=10, sticky='w')

        ttk.Separator(self.win, orient='horizontal').grid(row=4, columnspan=2, sticky='ew', padx=(25,0))

        # Label: Saving Preferences:
        Save_title_label = tk.Label(self.win, text="Saving Preferences:", font=self.font, bg=self.bg_color, fg=self.fg_color)
        Save_title_label.grid(row=5, column=0, padx=10, pady=10, sticky='w')

        # Group Size
        display_a_label = tk.Label(self.win, text="Group Size:", font=self.font, bg=self.bg_color, fg=self.fg_color)
        display_a_label.grid(row=6, column=0, padx=10, pady=10, sticky='w')
        self.group_var = tk.IntVar()
        self.group_var.set(self.preferences.group_size)
        self.group_spinbox = self.separator_spinbox = tk.Spinbox(self.win, from_=1, to=10, increment=1, width=5, bg=self.bg_color, textvariable=self.group_var, command=lambda: self.option_changed(0))
        self.group_spinbox.grid(row=6, column=1, padx=10, pady=10, sticky='w')

        # Space between groups
        display_a_label = tk.Label(self.win, text="Space between groups:", font=self.font, bg=self.bg_color, fg=self.fg_color)
        display_a_label.grid(row=7, column=0, padx=10, pady=10, sticky='w')
        self.space_var = tk.StringVar()
        self.space_dropdown = self.dropdown(self.space_var, 'False', 'True',  self.preferences.group_space)
        self.space_dropdown.grid(row=7, column=1, padx=10, pady=10, sticky='w')

        # Separator length
        display_a_label = tk.Label(self.win, text="Separator length:", font=self.font, bg=self.bg_color, fg=self.fg_color)
        display_a_label.grid(row=8, column=0, padx=10, pady=10, sticky='w')
        self.separator_var = tk.IntVar()
        self.separator_var.set(self.preferences.separator_length)
        self.separator_spinbox = tk.Spinbox(self.win, from_=4, to=100, increment=3, width=5, bg=self.bg_color, textvariable=self.separator_var, command=lambda: self.option_changed(0))
        self.separator_spinbox.grid(row=8, column=1, padx=10, pady=10, sticky='w')

        # Cancel/save buttons (within a frame)
        button_frame = tk.Frame(self.win, bg=self.bg_color)
        button_frame.grid(row=9, column=0, columnspan=2, sticky='e')
        self.save_button = tk.Button(button_frame, text="Save", underline=0, bg=self.btn_color, state='disabled', font=self.font, command=lambda: self.save_changes(0))
        self.save_button.pack(side='right', padx=10, pady=20)
        self.cancel_button = tk.Button(button_frame, text="Cancel", underline=0, bg=self.btn_color, font=self.font, command=lambda: self.cancel_setup(0))
        self.cancel_button.pack(side='right', padx=10, pady=20)

        # Keyboard shortcuts
        self.win.bind('<Escape>', self.cancel_setup)
        self.win.bind(',', self.cancel_setup)
        self.win.bind('c', self.cancel_setup)


    def dropdown(self, string_var, option1, option2, setting_change):
        # Creates dropdown options. If I need more than two options, change to dictionary {1:'s', 2:'s', etc.}

        if setting_change:
            string_var.set(option2)
        else:
            string_var.set(option1)

        dd = tk.OptionMenu(self.win, string_var, option1, option2, command=self.option_changed)
        dd['menu'].config(bg=self.bg_color, fg=self.fg_color, font=self.font)
        dd.config(bg=self.bg_color, fg=self.fg_color, font=self.font)
        return dd


    def cancel_setup(self, e):
        self.win.destroy()


    def option_changed(self, e):
        self.save_button['state'] = 'normal'
        self.win.bind('s', self.save_changes)


    def save_changes(self, e):
        if self.order_var.get() == "Random":
            self.preferences.random = 1
        else:
            self.preferences.random = 0

        if self.answer_first_var.get() == "Answers":
            self.preferences.reversed = 1
        else:
            self.preferences.reversed = 0

        if self.counter_var.get() == 'Disable':
            self.preferences.counter_off = 1
        else:
            self.preferences.counter_off = 0

        if self.display_a_var.get() == 'Single':
            self.preferences.single_mode = 1
        else:
            self.preferences.single_mode = 0

        self.preferences.group_size = self.group_var.get()

        if self.space_var.get() == 'True':
            self.preferences.group_space = 1
        else:
            self.preferences.group_space = 0

        self.preferences.separator_length = self.separator_var.get()

        self.preferences.write_file()
        self.win.destroy()
