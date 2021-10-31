import os.path
from random import shuffle


class Quiz():
    """Class that holds the parsed questions and answers"""
    
    def __init__(self, file_dir=''):
        self.questions = []
        self.answers = []
        self.file_dir = file_dir
        self.filename = os.path.basename(file_dir)
        self.length = 0
        self.location = 0
        self.index = ''
        self.quiz = []
        self.qf_type = True # False if file does not have any Q: A: lines
        self.encoding_error = False

        if self.file_dir:
            self._parse_lines()

            # A separate list for random order
            self.random_feed = list(self.quiz)
            shuffle(self.random_feed)


    def _parse_lines(self):
        try:
            with open(self.file_dir, encoding='utf-8') as f:
                lines = f.readlines()

            # Get all the Q&As into one list, with multilines
            questions_and_answers = [' ']  # Space added in case of blank lines before first Q:
            for line in lines:
                if line.startswith('----'):
                    continue
                elif line.startswith(("Q: ", "A: ")):
                    questions_and_answers.append(line)
                else:
                    questions_and_answers[-1] += line

            # First item removed:
            questions_and_answers = questions_and_answers[1:]

            # Divide them into two lists and strip Q: A: codes
            for q_a in questions_and_answers:
                if q_a.startswith('Q: '):
                    self.questions.append(q_a[3:])
                elif q_a.startswith('A: '):
                    self.answers.append(q_a[3:])

            self.length = len(self.questions)

            if self.length == 0:
                self.qf_type = False
                self._parse_not_qf(lines)
                return

            # Combine questions and answers into tuple pairs. test: Use zip instead?
            for idx in range(self.length):
                self.quiz.append((self.questions[idx], self.answers[idx]))
        except UnicodeDecodeError:
            self.encoding_error = True


    def _parse_not_qf(self, lines):
        line_hold = ''
        num = 0
        # Can't use .enumerate() since it skips blank lines
        for l in lines:
            if l.strip():
                if (num % 2) == 0:
                    line_hold = l.strip()
                    num += 1
                else:
                    self.quiz.append((line_hold, l.strip()))
                    line_hold = ''
                    num += 1

        if line_hold:
            self.quiz.append(l)

        self.length = len(self.quiz)
