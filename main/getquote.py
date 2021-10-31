from itertools import cycle
from random import shuffle

class QuoteList(object):
    '''List of quotes, randomized'''

    def __init__(self, file_path):

        self.file_path = file_path
        self.quotes = []
        self.rand_quotes = []

        # Each non-empty line in file is one quote
        try:
            with open(self.file_path) as f:
                for line in f:
                    if line.strip():
                        self.quotes.append(line)
        except FileNotFoundError as e:
            with open(self.file_path, 'w') as f:
                pass

        # Create a new randomized copy of quotes
        self.rand_quotes = self.quotes[:]
        shuffle(self.rand_quotes)

        # Create generator loops
        self.quotes = cycle(self.quotes)
        self.rand_quotes = cycle(self.rand_quotes)

    def get_next_random_quote(self):
        try:
            return next(self.rand_quotes)
        except StopIteration:
            return "Quotes file empty.\nAdd your quotes to quotes.txt file in data directory.\nOne line per quote."


    def get_next_quote(self):
        try:
            return next(self.quotes)
        except StopIteration:
            return "Quotes file empty.\nAdd your quotes to quotes.txt file in data directory.\nOne line per quote."
