from tkinter import *
from tkinter import ttk
from googletrans import Translator
import pyperclip, threading
from time import sleep
from win32gui import EnumWindows, GetWindowText, SetForegroundWindow
from win32com.client import Dispatch
from os import getcwd
from os.path import join
from json import load, dump
from win32api import GetCursorPos
from tkinter import messagebox
from random import choice

class Frame(object):

    def __init__(self):
        self.root_path = getcwd()
        self.path_configuration = join(self.root_path, 'config.json')
        with open((self.path_configuration), 'r', encoding='utf8') as fp:
            self.configuration = load(fp)
        self.user_agent = self.configuration['user_agent']
        self.thread = threading.Thread(target=(self.task), args=())
        self.is_running = True
        service_urls = []
        service_urls.append(self.configuration['current source'])
        self.translator = Translator(service_urls=service_urls, user_agent=(choice(self.user_agent)))
        self.shell = Dispatch('WScript.Shell')
        self.prior_paste = pyperclip.paste()
        self.window = Tk()
        self.window.wm_attributes('-toolwindow', True)
        self.window.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.window.winfo_toplevel().title('Translator')
        self.comboxlist_source = ttk.Combobox(self.window)
        self.comboxlist_source['values'] = tuple(self.configuration['source'])
        try:
            source = self.configuration['source'].index(self.configuration['current source'])
        except ValueError:
            source = 0

        self.comboxlist_source.current(source)
        self.comboxlist_source.bind('<<ComboboxSelected>>', self.select_source)
        self.comboxlist_language = ttk.Combobox(self.window)
        language_list = []
        for item in self.configuration['language map']:
            language_list.append(item)

        language_tuple = tuple(language_list)
        self.comboxlist_language['values'] = language_tuple
        try:
            language = language_tuple.index(self.configuration['current language'])
        except ValueError:
            language = 0

        self.comboxlist_language.current(language)
        self.comboxlist_language.bind('<<ComboboxSelected>>', self.select_language)
        self.scrollbar = Scrollbar(self.window)
        self.text = Text((self.window), height=8, width=50, font=('microsoft yahei',
                                                                  10, 'bold'))
        self.copy_button = Button((self.window), text='Copy', command=(self.copy))
        self.label_source = Label((self.window), text='Source')
        self.label_language = Label((self.window), text='Language')
        self.text.grid(row=0, column=0, columnspan=3)
        self.scrollbar.grid(row=0, column=3, sticky='NS')
        self.copy_button.grid(row=1, columnspan=4, sticky='WE')
        self.label_source.grid(row=2, column=0)
        self.comboxlist_source.grid(row=2, column=1, columnspan=3, sticky='WE')
        self.label_language.grid(row=3, column=0)
        self.comboxlist_language.grid(row=3, column=1, columnspan=3, sticky='WE')
        self.scrollbar.config(command=(self.text.yview))
        self.text.config(yscrollcommand=(self.scrollbar.set))
        self.hwnd = None
        self.translation = None
        self.text_display = ''

    def select_source(self, *args):
        source = self.comboxlist_source.get()
        self.configuration['current source'] = source
        service_urls = []
        service_urls.append(self.configuration['current source'])
        self.translator = Translator(service_urls=service_urls, user_agent=(choice(self.user_agent)))

    def select_language(self, *args):
        language = self.comboxlist_language.get()
        self.configuration['current language'] = language

    def copy(self):
        pyperclip.copy(self.text_display)

    def on_closing(self):
        if messagebox.askokcancel('Quit', 'Do you want to quit?'):
            with open((self.path_configuration), 'w', encoding='utf8') as fp:
                dump(self.configuration, fp)
            self.window.destroy()
            self.is_running = False

    def write(self, text):
        self.text.delete('1.0', END)
        self.text.insert(INSERT, text)

    def get_hwnd(self, name):
        hd = []

        def callback(hwnd, hd):
            if name == GetWindowText(hwnd):
                hd.append(hwnd)

        EnumWindows(callback, hd)
        if hd == []:
            raise Exception("can't find window")
        else:
            self.hwnd = hd[0]
        return hd[0]

    def SetForegroundWindow(self, hwnd=None):
        if hwnd == None:
            hwnd = self.hwnd
        self.shell.SendKeys('%')
        SetForegroundWindow(hwnd)

    def raise_above_all(self):
        self.window.attributes('-topmost', True)
        self.window.attributes('-topmost', False)

    def task(self):
        while self.is_running is True:
            sleep(0.1)
            paste = pyperclip.paste()
            if paste != self.prior_paste:
                break

        while True:
            if self.is_running is True:
                sleep(0.1)
                if self.hwnd is not None:
                    paste = pyperclip.paste()
                    if paste != self.prior_paste:
                        if paste not in self.text_display:
                            try:
                                self.translation = self.translator.translate(paste, dest=(self.configuration['language map'][self.configuration['current language']]))
                                self.text_display = ''
                                self.text_display += self.translation.text
                                self.text_display += '\n'
                                if len(self.translation.extra_data['translation'][1]) >= 4:
                                    pron = self.translation.extra_data['translation'][1][3]
                                    if pron is not None:
                                        self.text_display += '['
                                        self.text_display += pron
                                        self.text_display += ']'
                                self.write(self.text_display)
                            except:
                                self.write('Oops! A network error occured, please try later or change source.')

                            self.raise_above_all()
                            self.SetForegroundWindow()
                            x, y = GetCursorPos()
                            self.window.geometry('+%d+%d' % (x, y))
                    self.prior_paste = paste
                else:
                    try:
                        self.hwnd = self.get_hwnd(self.configuration['window name'])
                    except:
                        pass

            else:
                return

    def start(self):
        self.text_display = 'Welcome back!'
        self.write(self.text_display)
        self.thread.start()
        self.window.mainloop()


def list_windows():

    def callback(hwnd, para):
        print(GetWindowText(hwnd))

    EnumWindows(callback, None)


f = Frame()
f.start()