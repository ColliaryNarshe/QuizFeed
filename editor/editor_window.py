import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os.path

from editor.editor_file import QuizEdit
from main.quiz_parser import Quiz
from preferences.preferences_window import PreferencesWindow



class EditorWindow:
    def __init__(self, main_win, quiz='data/.tempeditor'):
        self.root = tk.Toplevel()
        self.root.focus_set()
        self.root.grab_set()
        self.width = main_win.root.winfo_screenwidth()
        self.height = main_win.root.winfo_screenheight()
        self.x, self.y = (self.width // 2) - 400, (self.height - 300) // 6
        self.root.geometry(f'+{self.x}+{self.y}')
        self.root.title("Create New QF File")
        self.root.config(bg=BG_COLOR)
        self.main_win = main_win

        # Get temp quiz if exists
        if os.path.exists(quiz):
            self.quiz_choice = Quiz(quiz)
        else:
            self.quiz_choice = Quiz()

        self.new_quiz = QuizEdit(self, main_win, self.quiz_choice)

        self.root.protocol("WM_DELETE_WINDOW", lambda: self.new_quiz.quit_editor(0))

        self.display_top_menu()
        self.display_status_bar()
        self.entry_boxes()
        self.display_buttons()
        self.keyboard_bindings()


    def keyboard_bindings(self):
        self.root.bind('<Control-Right>', self.new_quiz.next_question)
        self.root.bind('<Control-Left>', self.new_quiz.prev_question)
        self.root.bind('<Control-Down>', self.switch_focus)
        self.root.bind('<Control-Up>', self.switch_focus)
        self.root.bind('<Control-q>', self.new_quiz.quit_editor)

    def display_top_menu(self):
        # Menu
        self.top_menu = tk.Menu(self.root)
        self.root.configure(menu=self.top_menu)

        # File Menu
        self.file_menu = tk.Menu(self.top_menu, tearoff=False)
        self.top_menu.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='New Quiz', command=self.new_quiz.delete_all)
        self.file_menu.add_command(label='Load Quiz', command=self.load_quiz)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Save to File', accelerator='   Ctrl-S', command=self.new_quiz.save_to_disk)
        self.file_menu.add_command(label='Append to File', accelerator='   Ctrl-A', command=self.new_quiz.append_to_disk)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Treeview Selection')
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Temp Save and Quit', accelerator='   Ctrl-Q', command=lambda: self.new_quiz.quit_editor(0))
        self.file_menu.entryconfig('Treeview Selection', state='disabled')

        # Editor Menu
        self.editor_menu = tk.Menu(self.top_menu, tearoff=False)
        self.top_menu.add_cascade(label='Editor', menu=self.editor_menu)
        self.editor_menu.add_command(label='Insert New Question', command=lambda: self.new_quiz.insert_question(0))
        self.editor_menu.add_command(label='Delete Current Question', command=lambda: self.new_quiz.delete_question(0))
        self.editor_menu.add_separator()
        self.editor_menu.add_command(label='Next Question', accelerator="   Ctrl-Right", command=lambda: self.new_quiz.next_question(0))
        self.editor_menu.add_command(label='Previous Question', accelerator="   Ctrl-Left", command=lambda: self.new_quiz.prev_question(0))
        self.editor_menu.add_command(label='Switch Focus', accelerator="   Ctrl-Up, Ctrl-Down", command=lambda: self.switch_focus(0))
        self.editor_menu.add_separator()
        self.editor_menu.add_command(label='Jump to...', command=self.new_quiz.jump_to)

        # Tools menu
        self.tool_menu = tk.Menu(self.top_menu, tearoff=False)
        self.top_menu.add_cascade(label='Tools', menu=self.tool_menu)
        self.tool_menu.add_command(label='Preferences',
                                   command=lambda: self.preferences_window(0))


    def display_status_bar(self):
        self.status_bar = tk.Label(self.root, anchor='e', text="Question 1/1  ", bg="seashell4", relief=tk.SUNKEN, borderwidth=3, font=FONT)
        self.status_bar.pack(fill='x', side='bottom')
        self.new_quiz._update_status_bar()


    def entry_boxes(self):
        # Main Frame
        self.main_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.main_frame.pack()

        # Question label + entry box
        self.q_label = tk.Label(self.main_frame, text="Question:", font=FONT, bg=BG_COLOR, anchor='e')
        self.q_label.grid(row=0, padx=20, pady=(20,5), sticky='w')
        self.top_entry = tk.Text(self.main_frame, relief='ridge', bd=5, width=70, height=6, font=FONT, bg='grey80')
        self.top_entry.grid(pady=(0,10), padx=20, row=1)
        self.top_entry.focus_set()

        # Answer Label + entry box
        self.a_label = tk.Label(self.main_frame, text="Answer:", font=FONT, bg=BG_COLOR)
        self.a_label.grid(row=2, padx=20, pady=(10,5), sticky='w')
        self.bottom_entry = tk.Text(self.main_frame, relief='ridge', bd=5, width=70, height=6, font=('Helvetica', 16), bg='grey80')
        self.bottom_entry.grid(pady=(0,20), row=3)


    def display_buttons(self):
        self.button_frame = tk.Frame(self.root, bg=BG_COLOR) # Self to put Button frame inside self (this frame)
        self.button_frame.pack(side='right')

        insert_button = tk.Button(self.button_frame, text='Insert New', bg=BTN_COLOR, font=FONT, command=lambda: self.new_quiz.insert_question(0))
        del_button = tk.Button(self.button_frame, text='Delete', bg=BTN_COLOR, font=FONT, command=lambda: self.new_quiz.delete_question(0))
        prev_button = tk.Button(self.button_frame, text='Previous', bg=BTN_COLOR, font=FONT, command=lambda: self.new_quiz.prev_question(0))
        next_button = tk.Button(self.button_frame, text='Next', bg=BTN_COLOR, font=FONT, command=lambda: self.new_quiz.next_question(0))
        insert_button.grid(row=0, column=0, padx=(10,10), pady=(0,20))
        del_button.grid(row=0, column=1, padx=(10,100), pady=(0,20))
        prev_button.grid(row=0, column=2, padx=10, pady=(0,20))
        next_button.grid(row=0, column=3, padx=(10,20), pady=(0,20))


    def switch_focus(self, e):
        if self.root.focus_displayof() == self.top_entry:
            self.bottom_entry.focus_set()
        else:
            self.top_entry.focus_set()


    def load_quiz(self):
        if len(self.quiz_choice.quiz) > 2:
            if not messagebox.askyesno("Load File", "Are you sure you want to lose all current questions and open a new file?"):
                return
        filename =  filedialog.askopenfilename(title="Choose file", filetypes=(('text files', '*.txt'), ('all files', '*.*')))
        if not filename:
            return
        self.root.destroy()
        EditorWindow(self, self.main_win, filename)


    def preferences_window(self, e):
        PreferencesWindow(self.main_win.preferences)


FONT = ('Helvetica', 16)
BG_COLOR = 'seashell3'
BTN_COLOR = 'seashell4'
