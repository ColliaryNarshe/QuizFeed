import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from os import remove
import os.path

from main.quiz_parser import Quiz

class QuizEdit:
    def __init__(self, editor_window, main_win, quiz):
        self.quiz = quiz
        self.editor_window = editor_window
        self.location = len(self.quiz.quiz)
        self.main_win = main_win


    def next_question(self, e):
        # Get self.question and self.answer text from entries
        self._get_data()

        # If fields are empty:
        if not self.question and not self.answer:
            # If empty field is a new quiz, can't go forward:
            if self.location == len(self.quiz.quiz):
                return
            else:
                # If an old entry is empty, delete it:
                self._save_question(delete=True)
                self._update_entries()
                self._update_status_bar()
                return

        # Give default data if one entry left blank
        self._fill_blanks()

        # If it's a new question
        if self.location == len(self.quiz.quiz):
            self._save_question()
            self.location += 1
            self._update_entries()
            self._update_status_bar()

        # If viewing previous question
        else:
            self._save_question()
            self.location += 1
            self._update_entries()
            self._update_status_bar()


    def prev_question(self, e):
        # if at first question, can't go back:
        if not self.location:
            return

        # Get entry boxes
        self._get_data()

        # If fields are empty:
        if not self.question and not self.answer:
            # If not a new quiz, delete from quizes:
            if self.location != len(self.quiz.quiz):
                self._save_question(delete=True)
            self.location -= 1
            self._update_entries()
            self._update_status_bar()
            return

        # If text in one of the entry boxes, save it
        if self.question or self.answer:
            self._fill_blanks()
            self._save_question()

        self.location -=1
        self._update_entries()
        self._update_status_bar()


    def insert_question(self, e):
        self._get_data()

        # If end of list with no text, no need to insert:
        if self.location == len(self.quiz.quiz) and not self.question and not self.answer:
            return

        # Update current question
        if self.question or self.answer:
            self._save_question()

        # Insert new question
        self.question, self.answer = '<Blank>', '<Blank>'
        self._save_question(insert=True)
        self._update_entries()
        self._update_status_bar()


    def delete_question(self, e):
        self._get_data()

        # If end of list with no text, no need to delete:
        if self.location == len(self.quiz.quiz) and not self.question and not self.answer:
            return
        # If end of list with text, delete text:
        elif self.location == len(self.quiz.quiz):
            self.editor_window.top_entry.delete(0.0, 'end')
            self.editor_window.bottom_entry.delete(0.0, 'end')
            return
        #Delete text and quiz from list, update screen:
        else:
            del self.quiz.quiz[self.location]
            self._update_entries()
            self._update_status_bar()


    def delete_all(self):
        if len(self.quiz.quiz) > 1:
            self.main_win.root.withdraw()
            if not messagebox.askyesno("New File", "You will lose all unsaved questions. Continue?"):
                self.main_win.root.deiconify()
                return
            self.main_win.root.deiconify()

        self.quiz.quiz = []
        self.location = 0
        self._update_entries()
        self._update_status_bar()


    def jump_to(self):
        JumpWindow(self)


    def save_to_disk(self):
        self._get_data()
        if self.question or self.answer:
            self._fill_blanks()
            self._save_question()

        print(self.quiz.quiz)
        self.main_win.save_to_disk(self.quiz.quiz, 'New Quiz.txt')


    def append_to_disk(self):
        self._get_data()
        if self.question or self.answer:
            self._fill_blanks()
            self._save_question()

        self.main_win.save_to_disk(self.quiz.quiz, 'New Quiz.txt', append=True)


    def quit_editor(self, e):
        self._get_data()
        if self.question or self.answer:
            self._fill_blanks()
            self._save_question()

        if not len(self.quiz.quiz):
            if os.path.exists('data/.tempeditor'):
                remove('data/.tempeditor')
        else:
            self.main_win.save_to_disk(self.quiz.quiz, 'data/.tempeditor')

        self.editor_window.root.destroy()


    def _update_entries(self):
        self.editor_window.top_entry.delete(0.0, 'end')
        self.editor_window.bottom_entry.delete(0.0, 'end')

        # If reached last question, nothing to insert:
        if not self.location == len(self.quiz.quiz):
            self.editor_window.top_entry.insert(0.0, self.quiz.quiz[self.location][0])
            self.editor_window.bottom_entry.insert(0.0, self.quiz.quiz[self.location][1])

        self.editor_window.top_entry.focus_set()


    def _save_question(self, delete=False, insert=False):
        # Delete old quiz if not last question
        if self.location != len(self.quiz.quiz) and not insert:
            del self.quiz.quiz[self.location]
        if not delete:
            self.quiz.quiz.insert(self.location, (self.question, self.answer))


    def _fill_blanks(self):
        if not self.question:
            self.question = "<blank>"
        if not self.answer:
            self.answer = "<blank>"


    def _get_data(self):
        self.question = self.editor_window.top_entry.get(0.0, 'end').strip()
        self.answer = self.editor_window.bottom_entry.get(0.0, 'end').strip()


    def _update_status_bar(self):
        status_bar_text = "Question " + str(self.location + 1) + "/" + str(len(self.quiz.quiz) + 1) + '  '
        self.editor_window.status_bar.config(text=status_bar_text)




class JumpWindow(tk.Toplevel):
    def __init__(self, quiz_edit):
        super().__init__()
        self.quiz_edit = quiz_edit
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()
        self.x, self.y = (self.width // 2) - 50, (self.height // 4)
        self.geometry(f'+{self.x}+{self.y}')
        self.grab_set()

        # Get list of index numbers
        index_list = [x + 1 for x in range(len(self.quiz_edit.quiz.quiz) + 1)]

        # Combobox
        self.jump_dropbox = ttk.Combobox(self, value=index_list, font=('Helvetica', 20), width=5)
        self.jump_dropbox.pack(padx=10, pady=10)
        self.jump_dropbox.current(self.quiz_edit.location)

        self.bind('<<ComboboxSelected>>', self._set_value)

    def _set_value(self, e):
        self.quiz_edit._get_data()
        if self.quiz_edit.question or self.quiz_edit.answer:
            self.quiz_edit._fill_blanks()
            self.quiz_edit._save_question()
        self.quiz_edit.location = int(self.jump_dropbox.get()) - 1
        self.quiz_edit._update_entries()
        self.quiz_edit._update_status_bar()
        self.destroy()
