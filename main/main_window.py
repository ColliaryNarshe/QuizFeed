import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import ImageTk, Image
import os.path
from glob import glob
from itertools import cycle
from os import remove

from main.aggregator import main as aggregator
from main.anki_converter import convert_anki
from main.getquote import QuoteList
from main.quiz_parser import Quiz

from preferences.font_window import ChangeFont
from preferences.paths_window import PathsWindow
from preferences.preferences_manager import Preferences
from preferences.preferences_window import PreferencesWindow

from editor.editor_window import EditorWindow


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("QuizFeed")
        self.width = root.winfo_screenwidth()
        self.height = root.winfo_screenheight()
        self.x, self.y = (self.width // 2) -500, (self.height - 600) // 3
        self.root.geometry(f'1000x600+{self.x}+{self.y}')
        self.bg_color = 'black'
        self.fg_color = 'white'
        self.root.config(bg=self.bg_color)
        self.font = ('Consolas', 16) # Consolas has fixed character size for listbox alignment
        self.quizes = [] # complete list of Quiz class instances
        self.quizes_not_qf = [] # Only the quizes that are not qf format
        self.quiz_choice = ''
        self.saved_qs = []
        self.preferences = Preferences(self)
        self.quiz_screen = '' # Instance
        self.quotes = QuoteList('data\\quotes.txt')
        self.photos = glob('images\\display\\*')
        self.nums = cycle([i for i in range(len(self.photos))]) # For photo index
        self.saves_running = False

        self.tempsaves_filename = 'data/.tempsaves'

        # Save settings (font size) and save files (if any) when quit
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.quit_program(0))

        self.create_top_menu()
        self.create_window_layout()
        self.create_keyboard_bindings()
        self.display_filenames()


    def create_top_menu(self):
        self.top_menu = tk.Menu(self.root)
        self.root.configure(menu=self.top_menu)

        # File: Backup Saved Questions, Add Directory Path, Exit
        self.file_menu = tk.Menu(self.top_menu, tearoff=False)
        self.top_menu.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='Show All Files',
                                   accelerator='   V',
                                   command=lambda: self.toggle_show_files(0))
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Quiz Editor', command=self.run_editor)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Backup Saved Questions',
                                   command=lambda: self.backup_saves())
        self.file_menu.add_command(label='Clear Saved Questions',
                                   command=self.ask_clear_saved)
        self.file_menu.add_command(label='Run Saved Questions',
                                   command=self.run_saved)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Add Directory Path',
                                   accelerator='   P',
                                   command=lambda: self.paths_window(0))
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Delete File',
                                   command=self.delete_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit',
                                   accelerator='   Ctrl-Q',
                                   command=lambda: self.root.quit())
        self.file_menu.entryconfig('Backup Saved Questions', state='disabled')
        self.file_menu.entryconfig('Clear Saved Questions', state='disabled')
        self.file_menu.entryconfig('Run Saved Questions', state='disabled')

        # Change show all menu label depending on setting
        if self.preferences.show_all_files:
            self.file_menu.entryconfig('Show All Files', label='Show Only QF Files')

        # Quiz
        self.quiz_menu = tk.Menu(self.top_menu, tearoff=False)
        self.top_menu.add_cascade(label='Quiz', menu=self.quiz_menu)
        self.quiz_menu.add_command(label='Save Question',
                                   accelerator='   S',
                                   command=lambda: QuizScreen.save_current_q(self.quiz_screen,0))
        self.quiz_menu.add_command(label='Undo Saved Question',
                                   command=lambda: QuizScreen.undo_saved_q(self.quiz_screen))
        self.quiz_menu.add_separator()
        self.quiz_menu.add_command(label='Next',
                                   accelerator='   Ctrl-Right, Enter, Spacebar',
                                   command=lambda: QuizScreen.display_next(self.quiz_screen,0))
        self.quiz_menu.add_command(label='Previous',
                                   accelerator='   Ctrl-Left, Backspace',
                                   command=lambda: QuizScreen.display_previous(self.quiz_screen,0))
        self.quiz_menu.add_command(label='Skip 10',
                                   accelerator='   .',
                                   command=lambda: QuizScreen.skip_ahead(self.quiz_screen, 0))
        self.quiz_menu.add_command(label='Back 10',
                                   accelerator='   ,',
                                   command=lambda: QuizScreen.skip_back(self.quiz_screen, 0))
        self.quiz_menu.add_separator()
        self.quiz_menu.add_command(label='Font Size',
                                   accelerator='   F',
                                   command=lambda: self.change_font(0))
        self.quiz_menu.add_separator()
        self.quiz_menu.add_command(label='Show Text Box',
                                   accelerator='   Ctrl-T',
                                   command=lambda: QuizScreen.toggle_textbox(self.quiz_screen,0))
        self.quiz_menu.add_separator()
        self.quiz_menu.add_command(label='Return to Menu',
                                   accelerator='   Esc',
                                   command=lambda: QuizScreen.return_to_menu(self.quiz_screen,0))
        self.top_menu.entryconfig('Quiz', state='disabled')
        self.quiz_menu.entryconfig('Undo Saved Question', state='disabled')

        # Tools: Preferences, Show Quote, Aggregate files, Convert Anki File
        self.tool_menu = tk.Menu(self.top_menu, tearoff=False)
        self.top_menu.add_cascade(label='Tools', menu=self.tool_menu)
        self.tool_menu.add_command(label='Preferences',
                                   accelerator='     R',
                                   command=lambda: self.preferences_window(0))
        self.tool_menu.add_separator()
        self.tool_menu.add_command(label='Show Quote',
                                   accelerator='     Ctrl-Y',
                                   command=lambda: self.display_quote(0))
        self.tool_menu.add_separator()
        self.tool_menu.add_command(label='Convert to QF format', command=self.convert_to_qf)
        self.tool_menu.add_command(label='Convert to Plain Text', command=self.convert_to_txt)
        self.tool_menu.add_separator()
        self.tool_menu.add_command(label='Aggregate Files', command=aggregator)
        self.tool_menu.add_command(label='Convert Anki File', command=self.anki_convert)
        self.tool_menu.entryconfig('Show Quote', state='disabled')


    def create_window_layout(self):
        # Status bar
        self.bottom_frame = tk.Frame(self.root, bg=self.bg_color)
        self.bottom_frame.pack(side=tk.BOTTOM, fill='x')

        self.status_bar = tk.Label(self.bottom_frame, anchor='e', text="QuizFeed v2.0  ", fg=self.bg_color, bg='grey60', relief=tk.SUNKEN, borderwidth=3, font=('Helvetica'))
        self.status_bar.pack(fill='x', side=tk.BOTTOM)

        # Main Frame for program
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack()

        # Title Labels for filename selection box
        self.filename_title = tk.Label(self.main_frame, text='Choose a file:', bg=self.bg_color, fg=self.fg_color, font=self.font, anchor=tk.W)
        self.filename_title.grid(column=0, row=0, pady=(100,10), padx=(10,0), sticky='W')
        self.saves_title = tk.Label(self.main_frame, text='Saves: ' + str(len(self.saved_qs)), bg=self.bg_color, fg=self.fg_color, font=self.font, anchor=tk.E)
        self.saves_title.grid(column=1, row=2, pady=(10,10), padx=(10,0), sticky='E')
        if self.saved_qs:
            self.saves_title.config(fg='red')
            self.file_menu.entryconfig('Backup Saved Questions', state='normal')
            self.file_menu.entryconfig('Clear Saved Questions', state='normal')
            self.file_menu.entryconfig('Run Saved Questions', state='normal')

        # Main Listbox for file selection
        self.listbox_scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL)
        self.file_listbox = tk.Listbox(self.main_frame, width=60, height=13, bg=self.bg_color, fg=self.fg_color, font=self.font, yscrollcommand=self.listbox_scrollbar.set, activestyle='none')
        self.file_listbox.grid(column=0, row=1, padx=(10,0), columnspan=2)
        self.listbox_scrollbar.config(command=self.file_listbox.yview)
        self.listbox_scrollbar.grid(column=3, row=1, sticky=tk.NS)
        self.file_listbox.focus_set()

        # Errors: Invisible message area to display any errors when loading files
        self.error_message = tk.Message(self.main_frame, width=800, bg=self.bg_color, fg='red', text='')
        self.error_message.grid(column=0, row=3, columnspan=4)


    def create_keyboard_bindings(self):
        self.file_listbox.bind('<Return>', self.start_quiz)
        self.file_listbox.bind('<Double-1>', self.start_quiz) # Double click
        self.root.bind('<Control-q>', self.quit_program)
        self.root.bind('r', self.preferences_window)
        self.root.bind('p', self.paths_window)
        self.root.bind('f', self.change_font)
        self.root.bind('v', self.toggle_show_files)
        self.root.bind('showimage', self.display_pic)


    def display_filenames(self):
        '''Gets list of quiz objects, adjust order, then displays them on screen'''

        self.get_quizes()

        for idx, q in enumerate(self.quizes):
            if q.location > 1 and not q.qf_type:
                name_with_size =  f"Cont: Single: {os.path.splitext(q.filename)[0]: <36}" + f"{q.location*2}/{q.length*2}".rjust(9)
            elif q.location > 1:
                nums = 0
                name_with_size =  f"Continue: {os.path.splitext(q.filename)[0]: <40}" + f"{q.location}/{q.length}".rjust(9)

            elif not q.qf_type:
                name_with_size =  f"Single format: {os.path.splitext(q.filename)[0]: <35}" + f"{q.length * 2}".rjust(9)

            else:
                name_with_size = f"{os.path.splitext(q.filename)[0]: <54}" + f"{q.length}".rjust(5)



            self.file_listbox.insert(tk.END, name_with_size)

            if not q.qf_type and q.location < 1:
                self.file_listbox.itemconfig(idx, {'fg':'yellow'})

            if q.location > 1:
                self.file_listbox.itemconfig(idx, {'fg':'blue'})


    def get_quizes(self):
        '''Gets quiz files from default dir and added paths, makes quiz objects
        returns them as a list.
        '''

        self.quizes = []

        # Default folder
        txt_file_names = glob('quizes/*.txt')

        # Add user directories, print error to screen for any that don't exist
        error_string = ''
        for path in self.preferences.dirs:
            if os.path.exists(path):
                txt_file_names += glob(path + '/*.txt')
            else:
                error_string += "\nPath not found: " + path

        self.error_message.config(text=error_string.strip())

        # Create Quiz object for each quiz
        idx = 0
        for f in txt_file_names:
            quiz = Quiz(f)

            # Print error if failed to load a file because of encoding
            if quiz.encoding_error:
                self.error_message['text'] += "\nEncoding Error: " + quiz.filename
                continue

            # Only add text files with quiz questions:
            if quiz.qf_type or self.preferences.show_all_files:
                self.quizes.append(quiz)
                quiz.index = idx
                idx += 1

            if not quiz.qf_type:
                self.quizes_not_qf.append(quiz)

            # Add saved locations from preferences to quizes:
            for p in self.preferences.cont_quizes:
                if quiz.filename == p[0]:
                    quiz.location = int(p[1])


    def run_saved(self):
        self.quiz_menu.entryconfig('Save Question', state='disabled')
        self.saves_running = True

        # Save the saved questions to disk in case edited
        with open(self.tempsaves_filename, 'w') as f:
            for pair in self.saved_qs:
                f.write("Q: " + pair[0].strip() + '\n' + "A: " + pair[1].strip() + '\n')

        self.quiz_screen = QuizScreen(self.root, self, Quiz(self.tempsaves_filename), self.preferences)


    def run_editor(self):
        EditorWindow(self)
        # root.withdraw() #If other window is closed, does it leave this running in background?
        # self.main_win.deiconify()


    def preferences_window(self, e):
        PreferencesWindow(self.preferences)


    def paths_window(self, e):
        PathsWindow(self.preferences, self)


    def start_quiz(self, e):
        # Get selected filename: (Returns tuple)
        selected_item_num = self.file_listbox.curselection()

        # Choose first item as default if <Return> pressed without selection
        if not selected_item_num:
            selected_item_num = (0,)

        self.quiz_choice = self.quizes[selected_item_num[0]]

        # Start quiz
        self.quiz_screen = QuizScreen(self.root, self, self.quiz_choice, self.preferences)


    def change_font(self,e):
        ChangeFont(self.preferences, self.quiz_screen)


    def convert_to_qf(self):
        selected_item_num = self.file_listbox.curselection()
        if not selected_item_num:
            return

        choice = self.quizes[selected_item_num[0]]
        filename = os.path.splitext(choice.filename)[0] + " (QF).txt"
        choice = self.quizes[selected_item_num[0]].quiz

        self.save_to_disk(choice, filename)
        self.reset_file_list()


    def convert_to_txt(self):
        selected_item_num = self.file_listbox.curselection()
        if not selected_item_num:
            return

        choice = self.quizes[selected_item_num[0]]
        filename = os.path.splitext(choice.filename)[0] + " (Plain).txt"
        choice = self.quizes[selected_item_num[0]].quiz

        self.save_to_disk(choice, filename, txt_convert=True)
        self.reset_file_list()


    def backup_saves(self):
        if self.quiz_choice:
            saves_filename = os.path.splitext(self.quiz_choice.filename)[0] + " (saves).txt"
        else:
            saves_filename = "Unknown (saves).txt"

        self.save_to_disk(self.saved_qs, saves_filename)
        self.ask_clear_saved()
        self.reset_file_list()


    def save_to_disk(self, quiz, filename, txt_convert=False, append=False):
        '''Takes quiz list of tuple pairs and default filename for save dialog box
           txt_convert True doesn't add A: Q: to lines'''

        if not quiz:
            return

        # Get save path or use a tempfile
        if filename == self.tempsaves_filename or filename =='data/.tempeditor':
            save_dir = filename
        else:
            default_path= os.path.abspath('.') + '/quizes'
            save_dir = tk.filedialog.asksaveasfilename(initialdir=default_path, initialfile=filename, title="Save file", filetypes=(('text files', '*.txt'), ('all files', '*.*')))
            if not save_dir:
                return

        # Save file if not canceled
        if not txt_convert:
            # Determin group size, spacing, and length of separator (between groups)
            if filename == self.tempsaves_filename or filename =='data/.tempeditor':
                group = 1
                # newlines between groups:
                nl = ''
                # Separator
                sp = ''
            else:
                group = self.preferences.group_size
                nl = '\n' * self.preferences.group_space
                if not self.preferences.separator_length:
                    sp = ''
                else:
                    sp = '\n' + '-' * self.preferences.separator_length

            if append:
                save_type = 'a'
            else:
                save_type = 'w'

            with open(save_dir, save_type) as f:
                # Save to file in groups of threes
                questions_group = ''
                answers_group = ''
                if append:
                    questions_group = '\n' + sp
                for count, pair in enumerate(quiz):
                    questions_group += '\nQ: ' + pair[0].strip()
                    answers_group += '\nA: ' + pair[1].strip()
                    if (count % group) == (group - 1):
                        f.write(questions_group + nl + answers_group + nl + sp)
                        questions_group, answers_group = '', ''
                # Last lines if any:
                if questions_group:
                    f.write(questions_group + "\n" + answers_group)

        # Text only, no Q: A: or spaces
        if txt_convert:
            with open(save_dir, 'w') as f:
                for l in quiz:
                    f.write(l[0].strip() + '\n' + l[1].strip() + '\n')


    def ask_clear_saved(self):
        if tk.messagebox.askyesno("Clear Saved", "Do you want to clear your saved questions?"):
            self.reset_saved_questions()


    def reset_saved_questions(self):
        self.saved_qs = []
        self.saves_title.config(fg='white', text='Saves: 0')
        self.file_menu.entryconfig('Backup Saved Questions', state='disabled')
        self.file_menu.entryconfig('Clear Saved Questions', state='disabled')
        self.file_menu.entryconfig('Run Saved Questions', state='disabled')

        if os.path.exists(self.tempsaves_filename):
            remove(self.tempsaves_filename)


    def reset_file_list(self):
        # Update the list of quizes in main menu.
        self.preferences.write_file()
        self.preferences = Preferences(self)
        self.file_listbox.delete(0,'end')
        self.display_filenames()


    def toggle_show_files(self, e):
        if self.preferences.show_all_files:
            self.preferences.show_all_files = 0
            self.file_menu.entryconfig('Show Only QF Files', label='Show All Files')
        elif not self.preferences.show_all_files:
            self.preferences.show_all_files = 1
            self.file_menu.entryconfig('Show All Files', label='Show Only QF Files')

        self.reset_file_list()


    def display_quote(self, e):
        quote_window = tk.Toplevel()
        quote_window.title('Quote')
        quote_window.geometry(f'+{self.x}+{self.y}')
        quote_window.config(bg=self.bg_color)
        quote_label = tk.Label(quote_window, text=self.quotes.get_next_random_quote(), wraplength=1000, font=self.font, bg=self.bg_color, fg=self.fg_color)
        quote_label.pack(padx=30, pady=30)
        quote_window.focus_set()

        def close(e):
            quote_window.destroy()

        quote_window.bind('<Control-y>', close)
        quote_window.bind('<Escape>', close)


    def display_pic(self, e):

        try:
            photo = ImageTk.PhotoImage(Image.open(self.photos[next(self.nums)]))
        except (FileNotFoundError, IndexError):
            return

        pic_window = tk.Toplevel()
        pic_window.focus_set()
        pic_window.title('Images')
        pic_window.geometry(f'+{self.x + 100}+0')
        pic_window.focus_set()
        self.tool_menu.entryconfig('Show Quote', state='normal')
        self.root.bind('<Control-y>', self.display_quote)

        pic_label = tk.Label(pic_window, image=photo)
        pic_label.photo = photo
        pic_label.pack()

        def close(e):
            pic_window.destroy()

        pic_window.bind('<Escape>', close)


    def anki_convert(self):
        filename =  filedialog.askopenfilename(title="Choose anki file", filetypes=(('text files', '*.txt'), ('all files', '*.*')))
        if filename:
            convert_anki(filename)


    def delete_file(self):
        selected_item_num = self.file_listbox.curselection()
        if not selected_item_num:
            return
        quiz = self.quizes[selected_item_num[0]]
        if tk.messagebox.askyesno('Delete File', "Are you sure you want "
                                f"to delete: {quiz.filename}?\nThis will permanantly remove "
                                "it from your computer.\nThis good file once lost "
                                "is lost forever."):
            os.remove(quiz.file_dir)
            self.reset_file_list()


    def quit_program(self, e):
        self.preferences.write_file()
        self.save_to_disk(self.saved_qs, self.tempsaves_filename)
        self.root.quit()



class QuizScreen:
    def __init__(self, root, quiz_feed_main, quiz, preferences):
        self.root = root
        self.quiz_feed_main = quiz_feed_main
        self.quiz_choice = quiz
        self.preferences = preferences
        self.root.geometry(f'1300x600+{self.quiz_feed_main.x - 150}+{self.quiz_feed_main.y}')
        self.bg_color = 'black'
        self.q_color = 'green'
        self.a_color = 'purple'
        self.displayed = True
        self.quiz_done = False
        self.texbox_prev = False # Flag used to keep text when viewing previous quiz
        self.textbox_data = ''

        self.quiz_screen_setup()
        self.display_next(0)


    def quiz_screen_setup(self):
        # Hide main menu (frame):
        self.quiz_feed_main.main_frame.pack_forget()

        # Text box for input
        self.text_frame = tk.Frame(self.quiz_feed_main.root, bg=self.bg_color)
        self.text_frame.destroy()

        # Change status bar text size:
        self.quiz_feed_main.status_bar.config(font=("Helvetica", 16))

        # Configure top menu (enable Quiz, disable Run Saved Questions)
        self.quiz_feed_main.top_menu.entryconfig('Quiz', state='normal')
        self.quiz_feed_main.file_menu.entryconfig('Run Saved Questions', state='disabled')

        # Main Frame for quiz
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill='both', expand=1)
        self.main_frame.focus_set() # For keyboard shortcuts

        # Delete Button
        if self.quiz_feed_main.saves_running:
            self.delete_button = tk.Button(self.main_frame, text="Delete", command=self.delete_saved)
            self.delete_button.pack(side='top')

        # Question and Answer text display widgets
        self.question_message = tk.Message(self.main_frame, font=self.preferences.quiz_font_size, bg=self.bg_color, fg=self.q_color, width=1200)
        self.question_message.pack(pady=(50,0), padx=20)

        self.answer_message = tk.Message(self.main_frame, font=self.preferences.quiz_font_size, bg=self.bg_color, fg=self.a_color, width=1200)
        self.answer_message.pack(pady=(50,0), padx=20)

        # Keyboard shortcuts
        self.main_frame.bind('<Escape>', self.return_to_menu)
        self.main_frame.bind('<Return>', self.display_next)
        self.main_frame.bind('<space>', self.display_next)
        self.main_frame.bind('<Control-Right>', self.display_next)
        self.main_frame.bind('<Button-1>', self.display_next)
        self.main_frame.bind('<Control-Left>', self.display_previous)
        self.main_frame.bind('<Button-3>', self.display_previous)
        self.main_frame.bind('<BackSpace>', self.display_previous)
        if not self.quiz_feed_main.saves_running:
            self.main_frame.bind('s', self.save_current_q)
        self.main_frame.bind(',', self.skip_back)
        self.main_frame.bind('.', self.skip_ahead)
        self.main_frame.bind('<Control-t>', self.toggle_textbox)
        self.main_frame.bind('<Button-2>', self.toggle_textbox)
        self.main_frame.bind('<MouseWheel>', self.mouse_wheel)


    def display_next(self, e):
        if self.displayed:

            # Remove the text from text box
            if self.text_frame.winfo_exists() and not self.texbox_prev:
                self.typing_box.delete(0.0, 'end')
                self.textbox_data = ''

            self.texbox_prev = False

            # if end of list, back to Main Menu
            if self.quiz_choice.location == (self.quiz_choice.length):
                self.quiz_done = True
                self.return_to_menu(0)
                return

            # Display question
            if self.preferences.random:
                self.quiz_pair = self.quiz_choice.random_feed[self.quiz_choice.location]
            else:
                self.quiz_pair = self.quiz_choice.quiz[self.quiz_choice.location]

            # Show Answers first setting:
            if self.preferences.reversed:
                self.quiz_pair = (self.quiz_pair[1], self.quiz_pair[0])

            self.answer_message.config(text='')
            self.question_message.config(text=self.quiz_pair[0], font=self.preferences.quiz_font_size)
            self.displayed = False
            self.update_status_bar()

        else:
            # Display Answer (Question redrawn in case font size changed)
            if self.preferences.single_mode or not self.quiz_choice.qf_type:
                self.question_message.config(text=self.quiz_pair[1], font=self.preferences.quiz_font_size)
            else:
                self.question_message.config(text=self.quiz_pair[0], font=self.preferences.quiz_font_size)
                self.answer_message.config(text=self.quiz_pair[1], font=self.preferences.quiz_font_size)
            self.displayed = True
            if not self.quiz_choice.qf_type:
                self.update_status_bar()
            self.quiz_choice.location += 1


    def display_previous(self, e):
        # Display the previous question
        if self.quiz_choice.location == 0:
            return
        self.displayed = True
        self.quiz_choice.location -= 1
        self.texbox_prev = True
        self.display_next(0)


    def skip_ahead(self, e):
        if self.quiz_choice.location >= (self.quiz_choice.length - 10):
            self.quiz_choice.location = self.quiz_choice.length - 1
        else:
            self.quiz_choice.location += 10
        self.displayed = True
        self.display_next(0)


    def skip_back(self,e):
        if self.quiz_choice.location <= 10:
            self.quiz_choice.location = 0
        else:
            self.quiz_choice.location -= 10
        self.displayed = True
        self.display_next(0)


    def update_status_bar(self, saved_q=False, unsaved_q=False):
        # Check counter on/off setting:
        if not self.preferences.counter_off:
            status_bar_text = "Count: " + str(self.quiz_choice.location + 1) + '/' + str(self.quiz_choice.length)
        else:
            status_bar_text = ''

        # Double the counting for text files that don't have Q: A:
        if not self.quiz_choice.qf_type:
            if self.displayed:
                status_bar_text = "Count: " + str((self.quiz_choice.location + 1) * 2) + '/' + str(self.quiz_choice.length * 2)
            else:
                status_bar_text = "Count: " + str(((self.quiz_choice.location + 1)* 2) - 1) + '/' + str(self.quiz_choice.length * 2)



        # Saves-count text added
        status_bar_text += "    Saves: " + str(len(self.quiz_feed_main.saved_qs)) + "  "

        # Add comment when a question is saved
        if saved_q:
            status_bar_text = "Question saved!   " + status_bar_text
        elif unsaved_q:
            status_bar_text = "Question removed!   " + status_bar_text

        # Update status bar:
        self.quiz_feed_main.status_bar.config(text=status_bar_text)


    def save_current_q(self, e):
        # Adds current quiz q/a pair to a list of saved questions
        if self.quiz_pair not in self.quiz_feed_main.saved_qs:
            self.a_question_saved = True
            self.quiz_feed_main.saved_qs.append(self.quiz_pair)
            self.quiz_feed_main.quiz_menu.entryconfig('Undo Saved Question', state='normal')
            self.update_status_bar(saved_q=True)
            self.quiz_feed_main.file_menu.entryconfig('Backup Saved Questions', state='normal')
            self.quiz_feed_main.file_menu.entryconfig('Clear Saved Questions', state='normal')
            self.quiz_feed_main.file_menu.entryconfig('Run Saved Questions', state='normal')


    def undo_saved_q(self):
        if self.a_question_saved:
            del self.quiz_feed_main.saved_qs[-1]
            self.a_question_saved = False
            self.quiz_feed_main.quiz_menu.entryconfig('Undo Saved Question', state='disabled')
            self.update_status_bar(unsaved_q=True)


    def delete_saved(self):

        # Delete a saved question from data/.tempsaves file when running saved questions
        if self.quiz_choice.quiz:
            del self.quiz_choice.quiz[self.quiz_choice.location]
            self.quiz_feed_main.saved_qs = self.quiz_choice.quiz
            self.quiz_choice.length -= 1

            with open('data/.tempsaves', 'w') as f:
                for pair in self.quiz_feed_main.saved_qs:
                    f.write("Q: " + pair[0].strip() + '\n' + "A: " + pair[1].strip() + '\n')

            # Reset the question
            if self.displayed:
                self.displayed = False
                if self.quiz_choice.location:
                    self.quiz_choice.location -= 1
            elif not self.displayed:
                self.displayed = True
                if self.quiz_choice.location:
                    self.quiz_choice.location -= 1

        if not self.quiz_choice.quiz:
            os.remove('data/.tempsaves')
            self.quiz_feed_main.file_menu.entryconfig('Run Saved Questions', state='disabled')
            self.return_to_menu(0)
        else:
            self.display_next(0)


    def toggle_textbox(self, e):
        if not self.text_frame.winfo_exists():
            self.text_frame = tk.Frame(self.quiz_feed_main.root, bg=self.bg_color)
            self.text_frame.pack(side=tk.BOTTOM, fill='x')
            self.typing_box = tk.Text(self.text_frame, height=5, bg='grey10',
                              fg='white', bd=3, relief='raised', font=('Helvetica', 18),
                              insertbackground='white')
            self.typing_box.pack(fill='x', side=tk.BOTTOM)
            self.typing_box.focus_set()
            self.toggle_key_bindings(False)
            self.quiz_feed_main.quiz_menu.entryconfig('Show Text Box', label="Hide Text Box")
            self.typing_box.insert(0.0, self.textbox_data[:-1])
        else:
            self.textbox_data = self.typing_box.get(0.0, 'end')
            self.text_frame.destroy()
            self.toggle_key_bindings(True)
            self.quiz_feed_main.quiz_menu.entryconfig('Hide Text Box', label="Show Text Box")
            self.main_frame.focus_set()


    def toggle_key_bindings(self, state):
        # Turn off all the shortcuts except for <Right> <Left>
        # Only the ones in root actually need to be disabled, but oh well.
        # Temporarily set arrows to root window

        if not state:
            self.typing_box.bind('<Control-t>', self.toggle_textbox)
            self.typing_box.bind('<Escape>', self.toggle_textbox)
            self.typing_box.bind('<Control-Right>', self.display_next)
            self.typing_box.bind('<Control-Left>', self.display_previous)
            self.main_frame.bind('<Right>', '')
            self.main_frame.bind('<Left>', '')
            self.main_frame.bind('<Escape>', '')
            self.main_frame.bind('<Return>', '')
            self.main_frame.bind('<space>', '')
            self.main_frame.bind('<BackSpace>', '')
            self.main_frame.bind('s', '')
            self.main_frame.bind(',', '')
            self.main_frame.bind('.', '')
            self.quiz_feed_main.root.bind('b', '')
            self.quiz_feed_main.root.bind('r', '')
            self.quiz_feed_main.root.bind('p', '')
            self.quiz_feed_main.root.bind('f', '')
            self.quiz_feed_main.root.bind('v', '')
        else:
            self.quiz_feed_main.root.bind('<Right>', '')
            self.quiz_feed_main.root.bind('<Left>', '')
            self.main_frame.bind('<Right>', self.display_next)
            self.main_frame.bind('<Left>', self.display_previous)
            self.main_frame.bind('<Escape>', self.return_to_menu)
            self.main_frame.bind('<Return>', self.display_next)
            self.main_frame.bind('<space>', self.display_next)
            self.main_frame.bind('<BackSpace>', self.display_previous)
            self.main_frame.bind('s', self.save_current_q)
            self.main_frame.bind(',', self.skip_back)
            self.main_frame.bind('.', self.skip_ahead)
            self.quiz_feed_main.root.bind('r', self.quiz_feed_main.preferences_window)
            self.quiz_feed_main.root.bind('p', self.quiz_feed_main.paths_window)
            self.quiz_feed_main.root.bind('f', self.quiz_feed_main.change_font)
            self.quiz_feed_main.root.bind('v', self.quiz_feed_main.toggle_show_files)


    def mouse_wheel(self, event):
        if event.delta < 0:
            self.display_next(0)
        elif event.delta > 0:
            self.display_previous(0)


    def return_to_menu(self, e):
        '''Adjusts all settings for the main menu'''

        # If quiz was finished with saved questions:
        if self.quiz_done and self.quiz_feed_main.saved_qs:
            self.quiz_feed_main.saves_title.config(fg='red')
            if tk.messagebox.askyesno('Quiz finished!', "Would you like to backup your saved questions?"):
                self.quiz_feed_main.backup_saves()

        # If there are saved questions before finishing:
        elif self.quiz_feed_main.saved_qs:
            self.quiz_feed_main.saves_title.config(fg='red')

        # Save unfinished location and edit the file menu (color and text)
        if not self.quiz_feed_main.saves_running:
            if self.quiz_done or self.quiz_choice.location < 3:
                self.quiz_choice.location = 0
                if self.quiz_choice.qf_type:
                    name_with_size = f"{os.path.splitext(self.quiz_choice.filename)[0]: <54}" + f"{self.quiz_choice.length}".rjust(5)
                else:
                    name_with_size = f"Single format: {os.path.splitext(self.quiz_choice.filename)[0]: <35}" + f"{self.quiz_choice.length * 2}".rjust(9)
                self.quiz_feed_main.file_listbox.delete(self.quiz_choice.index)
                self.quiz_feed_main.file_listbox.insert(self.quiz_choice.index, name_with_size)
                if self.quiz_choice.qf_type:
                    self.quiz_feed_main.file_listbox.itemconfig(self.quiz_choice.index, {'fg':'white'})
                else:
                    self.quiz_feed_main.file_listbox.itemconfig(self.quiz_choice.index, {'fg':'yellow'})
            else:
                if self.quiz_choice.qf_type:
                    name_with_size =  f"Continue: {os.path.splitext(self.quiz_choice.filename)[0]: <40}" + f"{self.quiz_choice.location}/{self.quiz_choice.length}".rjust(9)
                else:
                    name_with_size =  f"Cont: Single: {os.path.splitext(self.quiz_choice.filename)[0]: <36}" + f"{self.quiz_choice.location*2}/{self.quiz_choice.length*2}".rjust(9)

                self.quiz_feed_main.file_listbox.delete(self.quiz_choice.index)
                self.quiz_feed_main.file_listbox.insert(self.quiz_choice.index, name_with_size)
                self.quiz_feed_main.file_listbox.itemconfig(self.quiz_choice.index, {'fg':'blue'})

        # Reset and update settings for main menu window
        self.root.geometry(f'1000x600+{self.quiz_feed_main.x}+{self.quiz_feed_main.y}')
        self.quiz_feed_main.saves_running = False
        # Handle open textbox
        if self.text_frame.winfo_exists():
            self.text_frame.destroy()
            self.toggle_key_bindings(True)
            self.quiz_feed_main.quiz_menu.entryconfig('Hide Text Box', label="Show Text Box")
        # Top menu
        self.quiz_feed_main.quiz_menu.entryconfig('Save Question', state='normal')
        self.quiz_feed_main.top_menu.entryconfig('Quiz', state='disabled')
        self.quiz_feed_main.file_menu.entryconfig('Run Saved Questions', state='normal')
        # Status bar
        self.quiz_feed_main.saves_title.config(text='Saves: ' + str(len(self.quiz_feed_main.saved_qs)))
        self.quiz_feed_main.status_bar.config(font=("Helvetica", 12), text="QuizFeed 2.0  ")
        self.main_frame.pack_forget()
        self.quiz_feed_main.main_frame.pack()
        self.quiz_feed_main.file_listbox.focus_set()
