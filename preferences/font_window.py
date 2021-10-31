from tkinter import Toplevel, IntVar, Label, Spinbox, Button

class ChangeFont:
    def __init__(self, preferences, quiz_screen):
        self.preferences = preferences
        self.quiz_screen = quiz_screen
        self.win = Toplevel()
        self.win.geometry("+700+400")
        self.font = ('Helvetica', 16)
        self.win.focus_set()
        self.win.grab_set()

        self.current_size = IntVar()
        self.current_size.set(self.preferences.quiz_font_size[1])

        self.font_label = Label(self.win, text="Font size: ", font=self.font)
        self.font_label.grid(row=0, column=0, pady=20, padx=20)
        self.num_spinbox = Spinbox(self.win, from_=6, to=60, increment=3, textvariable=self.current_size, command=self.option_changed)
        self.num_spinbox.grid(row=0, column=1, columnspan=2, pady=20, padx=20)

        self.cancel_button = Button(self.win, text='Cancel', underline=0, command=self.win.destroy)
        self.cancel_button.grid(row=1, column=1, pady=20, sticky='E')
        self.save_button = Button(self.win, text='Save', command=lambda: self.save_font_size(0))
        self.save_button['state'] = 'disabled'
        self.save_button.grid(row=1, column=2, pady=20, padx=20, sticky='w')

        self.win.bind('c', self.canceled)
        self.win.bind('f', self.canceled)
        self.win.bind('<Escape>', self.canceled)

    def canceled(self, e):
        self.win.destroy()


    def option_changed(self):
        # Activates Button if Font value changed
        self.save_button['state'] = 'normal'

    def save_font_size(self, e):
        # Set new font to preferences
        self.preferences.quiz_font_size = ('Helvetica', self.num_spinbox.get(), 'bold')
        self.preferences.changes_made = True
        self.win.destroy()

        if self.quiz_screen.displayed:
            self.quiz_screen.displayed = False
            if self.quiz_screen.quiz_choice.location:
                self.quiz_screen.quiz_choice.location -= 1
        elif not self.quiz_screen.displayed:
            self.quiz_screen.displayed = True
            if self.quiz_screen.quiz_choice.location:
                self.quiz_screen.quiz_choice.location -= 1

        self.quiz_screen.display_next(0)
