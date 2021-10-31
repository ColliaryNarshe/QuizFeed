import os.path
from os import makedirs
import json
from main.quiz_parser import Quiz

class Preferences:
    def __init__(self, quiz_feed_main):
        self.quiz_feed_main = quiz_feed_main
        self.dirs = []
        self.random = 0
        self.reversed = 0
        self.counter_off = 0
        self.quiz_font_size = ('Helvetica', 18, 'bold')
        self.show_all_files = 0 # Show all files, not just QF format texts (Q: A: )
        self.single_mode = 0
        self.cont_quizes = []
        self.tempsaves_filename = 'data/.tempsaves'
        self.group_size = 3
        self.group_space = 1
        self.separator_length = 4

        self._create_directories()
        self._get_saved()
        self._get_data()


    def _create_directories(self):
        """Creates data, display, and quizes directories if they don't exist."""

        if not os.path.isdir('data'):
            makedirs('data')

        if not os.path.isdir('quizes'):
            makedirs('quizes')

        if not os.path.isdir('images/display'):
            makedirs('images/display')


    def _get_saved(self):
        # Parses the saved questions from previous session and add to saved_qs
        if os.path.exists(self.tempsaves_filename):
            self.quiz_feed_main.saved_qs = Quiz(self.tempsaves_filename).quiz


    def _get_data(self):
        """Get the saved settings, and directory paths"""

        # Create new file if necessary:
        if not os.path.exists('data/settings.json'):
            self.write_file()
            return

        with open('data/settings.json') as f:
            pref_dict = json.load(f)

        self.random = pref_dict['random']
        self.reversed = pref_dict['reversed']
        self.counter_off = pref_dict['counter_off']
        self.quiz_font_size = ('Helvetica', pref_dict['font_size'], 'bold')
        self.show_all_files = pref_dict['show_all']  # Show all files or only QF files (Q: A: )
        self.single_mode = pref_dict['single_mode']  # Single or Dual mode
        self.group_size = pref_dict['group_size']  # Alernating groups of Q&A size)
        self.group_space = pref_dict['group_space']  # Spacing between groups
        self.separator_length = pref_dict['separator_length']

        # Append filename, location
        for name, location in pref_dict['saved_quiz_locations'].items():
            self.cont_quizes.append([name, location])

        self.dirs = pref_dict['added_directories']


    def write_file(self):

        saved_quiz_locations = {}
        for q in self.quiz_feed_main.quizes:
            if q.location:
                saved_quiz_locations[q.filename] = q.location

        # Add quizes that might have been removed because not qf format (with the not-show preference on)
        for q in self.quiz_feed_main.quizes_not_qf:
            if q.location and q.filename not in saved_quiz_locations:
                saved_quiz_locations[q.filename] = q.location

        pref_dict = {
            "random": self.random,
            'reversed': self.reversed,
            'counter_off': self.counter_off,
            'font_size': self.quiz_font_size[1],
            'show_all': self.show_all_files,  # Show all files or only QF files (Q: A: )
            'single_mode': self.single_mode,  # Single or Dual mode
            'group_size': self.group_size,  # Size of Q groups & A groups before alternating (saving)
            'group_space': self.group_space,  # Spacing between groups (when saving to file)
            'separator_length': self.separator_length,  # Length of -------- dividers
            'saved_quiz_locations': saved_quiz_locations,
            'added_directories': self.dirs
        }

        with open('data/settings.json', 'w') as f:
            json.dump(pref_dict, f, indent=4)
