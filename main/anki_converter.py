from re import sub
from tkinter import filedialog

def convert_anki(file):
    questions = []
    answers = []

    with open(file) as f:
        for line in f:
            line = sub('<div>', '\n', line)
            line = sub('</div>', ' ', line)
            line = sub('&nbsp', '', line)
            parts = line.split('\t')
            questions.append(parts[0])
            answers.append(parts[1:2])

    filename = filedialog.asksaveasfilename(title="Save file", filetypes=(('text files', '*.txt'), ('all files', '*.*')))

    with open(filename, 'w') as new_file:
        for q, a in zip(questions, answers):
            new_file.write('Q: ' + str(q) + '\n')
            new_file.write('A: ' + str(a) + '\n')
