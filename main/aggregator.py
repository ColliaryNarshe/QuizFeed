# GUI app that allows multiple text files to be aggregated into a new .txt file.
# agg_files function can be imported from other scripts
# agg_all_files is meant to be called from command line. Aggregates all files in default dir
# python -c 'import agg; agg.agg_all_files()'

from glob import glob
import os.path
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from os import startfile
import time


def agg_all_files():
    '''
    Meant to be called from command line. Uses current directory.
    python -c 'import agg.py; agg.agg_all_files()'
    Aggregates all .txt files in a dir to a new .txt.
    '''
    txt_files = glob('./*.txt')
    print("\nYou are about to aggregate the following files:")
    for f in txt_files:
        print(f)
    choice = input("type: y/n\n>>> ")
    if choice in ['y', 'yes', 'Y', 'YES']:
        agg_files(txt_files)
        print("New aggregated file created.")
    else:
        print("Operation canceled.")
        return


def agg_files(file_list):
    '''
    Aggregates all given .txt file content into a new file.
    Saves to location of first file in list.
    '''

    # Before creating new text file, check file_list.
    for f in file_list:
        if not os.path.exists(f):
            raise Exception("File doesn't exist")
        if f[-4:] != '.txt':
            raise Exception("File must be .txt file")

    save_dir = os.path.dirname(file_list[0])

    # Check for unique name and save file.
    filename = 'aggregation_file 01.txt'
    num = 1
    while num < 200:
        if os.path.exists(save_dir + '/' + filename):
            num += 1
            filename = 'aggregation_file ' + str(num).zfill(2) + '.txt'
        else:
            with open(save_dir + '/' + filename, 'w', encoding='utf-8') as new_file:
                new_file.write("Files: " + str(file_list) + '\n-----\n')
                for f in file_list:
                    to_copy = open(f, encoding='utf-8').read()
                    new_file.write(f"Below is {f} file:\n\n{to_copy}\n-----\n")
            break


def main():
    root = tk.Toplevel()
    root.title("Text File Aggregation")
    root.geometry("+600+200")
    bg_color = 'seashell2'
    bg_drk_color = 'seashell3'
    button_color = 'light steel blue'
    root.configure(bg=bg_color)
    root.dirname = os.path.expanduser('~')
    root.focus_set()

    def ask_dir(event):
        '''Gets the new directory from user, removes old displayed list and
        calls display_file_boxes() to display new list.'''


        global check_button_list

        new_dir = filedialog.askopenfilename(initialdir=root.dirname, title="Select a text file.")
        new_dir = os.path.dirname(new_dir)

        root.focus_set()

        # check if filedialog was canceled, else set new directory
        if not new_dir:
            return
        else:
            root.dirname = new_dir

        for btn in check_button_list:
            btn.destroy()

        root.string_dir.set(os.path.abspath(root.dirname)[-41:])

        display_file_boxes()


    def display_file_boxes():
        '''Display the list of files as check boxes'''

        # Dictionary to save the status of checkbutton: 1/0
        global check_dict
        global check_button_list

        check_dict = {}
        check_button_list = []

        root.filenames = glob(root.dirname + '/*.txt')
        
        # if not root.filenames:
        #     root.geometry('695x180')
        #     return
        #
        # # y adds 44 for each filebox line
        # new_y = 255 + (44 * len(root.filenames))
        # root.geometry('695x' + str(new_y))

        for f in root.filenames:
            check_dict[f] = tk.IntVar()

            # Create the check buttons
            btn = tk.Checkbutton(file_frame, variable=check_dict[f],
                                text=os.path.basename(f), bg=bg_drk_color, padx=20,
                                activebackground=bg_drk_color)
            btn.pack(anchor='w')
            check_button_list.append(btn)

        # Couldn't .select() buttons in above for-loop, had to make a separate list.
        for button in check_button_list:
            button.select()

        root.focus_set()


    def agg_files_button(event):
        '''Calls agg_files() with chosen files, then updates list'''

        global check_dict
        global check_button_list
        chosen_files = []

        for f in check_dict:
            if check_dict[f].get():
                chosen_files.append(f)

        if len(chosen_files) < 2:
            messagebox.showwarning('Insufficient files', 'You must choose two or more files.')
            return

        choice = messagebox.askokcancel('Aggregate', "Are you sure you want "
                                        "to Aggregate these files?")

        if choice:
            progress_win()
            agg_files(chosen_files)
            os.startfile(root.dirname)
            for btn in check_button_list:
                btn.destroy()
            display_file_boxes()


    def progress_win():
        progress_win = tk.Toplevel()
        progress_win.config(bg='white')
        progress_win.title("Creating your file.")
        pb = ttk.Progressbar(progress_win, length=300, mode='determinate')
        pb.pack(ipady=20)
        progress_label = tk.Label(progress_win, bg='white', text='', font=('Helvetica', 14))
        progress_label.pack()

        for p in range(20):
            pb['value'] += 5
            progress_label.config(text="File completion: " + str(int(pb['value'])) + '%')
            time.sleep(.2)
            root.update_idletasks()

        #Had to add this string to completely remove previous string, not sure why
        progress_label.config(text='                                        ')
        root.update_idletasks()
        progress_label.config(text="Your file is complete!")
        root.update_idletasks()
        time.sleep(.5)
        progress_win.destroy()


    # Button to change directory
    dir_select_button = tk.Button(root, text="Browse...", bd=5,
                                  bg=button_color, font=('Arial', 12, 'bold'),
                                  command=lambda: ask_dir(1))
    dir_select_button.grid(row=1, column=0, padx=10, pady=(40,0), sticky='w')

    # Entry: Displays current directory
    root.string_dir = tk.StringVar()
    root.string_dir.set(os.path.abspath(root.dirname))
    dir_label = tk.Entry(root, bg=bg_drk_color, textvariable=root.string_dir,
                         font=('Arial', 12, 'bold'), width=50)
    dir_label.grid(row=1, column=1, sticky='we', columnspan=2, padx=10, pady=(40,0))

    # Create frame for filenames
    file_frame = tk.Frame(root, bg=bg_drk_color, bd=10, highlightbackground='black', highlightthickness=3)
    file_frame.grid(row=3, column=0, columnspan=2, padx=10, sticky='w')
    empty_label = tk.Label(file_frame, width=54, bg=bg_drk_color)
    empty_label.pack(side='bottom')

    display_file_boxes()

    # Button to make aggregate file
    choice_button = tk.Button(root, text="A\u0332ggregate", bg=button_color, bd=5,
                              font=('Arial', 12, 'bold'),
                              command=lambda: agg_files_button(1))
    choice_button.grid(row=2, column=0, pady=20, padx=10, columnspan=2)

    # Sets keyboard shortcuts
    root.bind('<Return>', ask_dir)
    root.bind('a', agg_files_button)

    root.mainloop()


if __name__ == '__main__':
    main()
