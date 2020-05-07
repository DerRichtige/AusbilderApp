from kivy.app import App
from kivy.lang import Builder
from receivingReportBanner import ReportBanner
from pdfbanner import PdfBanner
from CheckEmails import CheckEmailsPopup
from kivy.properties import StringProperty, ObjectProperty
from azubibanner import AzubiBanner
from kivy.clock import Clock
from PyPDF2 import PdfFileReader
from custwidgets import *
from os import listdir
import screens
from kivy.factory import Factory
import os
import time
import re
import json
import subprocess
import threading


class BerichtsheftApp(App):
    """
    Is a subclass of the App class, which is the base of the application and
    it's the main entry point into the Kivy run loop.

    Attributes
    ----------
    txt_dct : dictionary
        To change header text according to the screen name
    checked_reports : list
        Contains all new received reports
    MY_FIRST_NAME : str
        The first name of the user
    MY_LAST_NAME : str
        The last name of the user
    MY_EMAIL : str
        The e-mail of the user
    stop_it : threading.Event
        manages an internal flag that can be set to true
    counter : int
        Used to count the number of received PDF files

    Methods
    -------
    check_emails()
        Open a popup that asks for the email password to check the Inbox.
    build()
        Initializes the application
    open_error_popup(message)
        Open a popup to show the error message.
    completed_pdf_banners(year)
        Search for completed PDF files
    add_completed_pdf_files(azubi_name, year, completed_pdf_folder,
                            pdfbanner_grid)
        Add completed PDF files to a scroll view
    update_overview_screen(azubi_name)
        Updates overview.
    check_new_reports()
        check if a new report has arrived.
    update_homescreen()
        Check every 10 seconds if a new completed report appeared.
    on_stop()
        The Kivy event loop is about to stop, set a stop signal.
    on_start()
        Get everything ready to start the app correctly
    check_received_reports()
        Update the homescreen
    update_db(email, azubi, max_reports)
        Update the database with data from the new trainee.
    del_received_report(id_number, rep)
        Delete the passed report in the scroll view in the homescreen.
    update_azubi_list()
        Update the azubiscreen.
    save_signature()
        Change trainee_signature in the database to True.
    change_screen(screen_name)
        Change current screen to a passed screen.
    is_filled_out()
        Check if user data input is valid and completely.
    save_infos(popup=True)
        Analyze the entered user data for validity and update the user data.
    """
    txt_dct = {'home_screen': 'HOME',
               'settings_screen': 'EINSTELLUNGEN',
               'azubi_screen': 'AUSZUBILDENDE'}
    counter = 0
    checked_reports = []
    stop_it = threading.Event()  # default is False
    # Check if a database already exists
    if not os.path.isfile(os.path.join(os.getcwd(), 'data', 'Data.json')):
        # User data
        MY_FIRST_NAME = ''
        MY_LAST_NAME = ''
        MY_EMAIL = ''
    else:
        # Initiate variables with data in the database
        with open(os.path.join(os.getcwd(), 'data', 'Data.json'), 'r') as f:
            data = json.load(f)
        # User data
        MY_FIRST_NAME = data['info']['first_name']
        MY_LAST_NAME = data['info']['last_name']
        MY_EMAIL = data['info']['my_email']

    def check_emails(self):
        """Open a popup that asks for the email password to check the Inbox."""
        CheckEmailsPopup().open()

    def build(self):
        """
        Initializes the application

        Override the default build method.
        Returns the constructed widget tree and this will be used as
        the root widget and
        added to the window.
        """
        # The kv file is not loaded by name convention
        GUI = Builder.load_file(os.path.join(os.getcwd(), "kv", "main.kv"))
        return GUI

    def open_error_popup(self, message, *args):
        """Open a popup to show the error message.

        Parameters
        ----------
        message : str
            The error message
        """
        ErrorPopup(message).open()

    def completed_pdf_banners(self, year, *args):
        """
        Search for completed PDF files

        Search for completed PDF files and sorted them in list
        for a given apprenticeship year.
        And calls the function add_completed_pdf_files.

        Parameters
        ----------
        year : str
            The apprenticeship year

        Raises
        ------
        exception (IndexError, ValueError)
            There is a wrong file in the folder.
        """
        azubi_name = self.root.ids['overview_screen'].ids['azubi_name'].text
        try:
            completed_pdf_folder = \
                sorted(listdir(os.path.join('.',
                                            'Azubis',
                                            azubi_name,
                                            f'Nachweise_{year}')),
                       key=(lambda pdf: int(pdf[-6:-4]) if
                            pdf[-6].isdigit() else int(pdf[-5])))
            pdfbanner_grid = \
                (self.root.ids['finalizedbanner_screen']
                    .ids['pdfbanner_grid'])

            pdfbanner_grid.clear_widgets()

        except (IndexError, ValueError):
            self.open_error_popup("OOPS, eine Datei im Ordner "
                                  "gehört "
                                  "dort nicht hin. "
                                  "Bitte Dort entfernen.")
        except Exception:
            self.open_error_popup("OOPS, ein Fehler ist aufgetreten.")
        self.add_completed_pdf_files(azubi_name, year, completed_pdf_folder,
                                     pdfbanner_grid)

    def add_completed_pdf_files(self,
                                azubi_name,
                                year,
                                completed_pdf_folder,
                                pdfbanner_grid):
        """
        Add completed PDF files to a scroll view

        Search every passed folder for completed PDF files of a given year
        and add for every completion a specific banner to the
        pdfbanner_grid.

        Parameters
        ----------
        azubi_name : str
            The name of the trainee
        year : str
            The apprenticeship year
        completed_pdf_folder : list
            All files from a folder which contains completed pdf files
        pdfbanner_grid : GridLayout
            Used to add Pdfbanner, which is a GridLayout,
            inside the pdfbanner_grid
            (is a child of the ScrollView Class)
        """
        self.root.ids['finalizedbanner_screen'].ids['title'].text = \
            f"Abgezeichnete Berichte - {year}. Lehrjahr"
        for pdf in completed_pdf_folder:
            with open(os.path.join(os.getcwd(),
                                   'Azubis',
                                   azubi_name,
                                   f'Nachweise_{year}',
                                   pdf),
                      'rb') as f:
                p = PdfFileReader(f)
                information = p.getDocumentInfo()
                c_w = information['/Calendar_week']
            f_num = pdf[-6:-4] if pdf[-6].isdigit() else pdf[-5]
            b = (PdfBanner(
                    azubi_name,
                    int(f_num),
                    int(year),
                    c_w_number=int(c_w)))
            pdfbanner_grid.add_widget(b)

    def update_overview_screen(self, azubi_name, *args):
        """Updates overview.

        Parameters
        ----------
        azubi_name : str
            The name of the trainee
        """
        self.root.ids['overview_screen'].ids['azubi_name'].text = azubi_name
        approved_reports = 0
        for num in range(1, 4):
            approved_reports += \
                len(listdir(os.path.join(os.getcwd(),
                                         'Azubis',
                                         azubi_name,
                                         f'Nachweise_{num}')))
        with open(os.path.join(os.getcwd(), 'data', 'Data.json'), 'r') as f:
            data = json.load(f)
        max_reports = \
            data['azubis'][azubi_name]['max_number_of_rep']
        self.root.ids['overview_screen'].ids['approved'].text = \
            f'{str(approved_reports)}/{str(max_reports)}'

    def check_new_reports(self, *args):
        """check if a new report has arrived."""
        new_rep = 0
        while True:
            # This is True only if the internal flag is True
            if self.stop_it.is_set():
                # Stop running this thread (main Python process can exit)
                return
            if (len(self.checked_reports) !=
                    len(listdir(os.path.join(os.getcwd(),
                                             'Received_Reports')))):
                Clock.schedule_once(self.check_received_reports)
            elif len(listdir(os.path.join(os.getcwd(),
                                          'Received_Reports'))) == new_rep:
                new_rep = None
                self.open_error_popup(
                    "Es sind keine neuen Berichte vorhanden.")
            time.sleep(5)  # blocking thread for 5 sec

    def update_homescreen(self, *args):
        """Check every 10 seconds if a new completed report appeared."""
        threading.Thread(target=self.check_new_reports,
                         daemon=True).start()

    def on_stop(self):
        """The Kivy event loop is about to stop, set a stop signal."""
        # Set the internal flag to True, which will stop
        # hanging threads when the app is about to close
        self.stop_it.set()
        with open(os.path.join(os.getcwd(), 'data', 'Data.json'), 'r') as f:
            data = json.load(f)
        if data['info']['valid'] is False:
            os.remove(os.path.join(os.getcwd(), 'data', 'Data.json'))

    def on_start(self):
        """
        Get everything ready to start the app correctly

        Check if it's the first time opening the app, if so
        open popup to get User data.
        And create or update the home screen and the database.

        Raises
        ------
        exception IOError
            File 'template.json' does not appear to exist
        """
        os.makedirs(os.path.join(os.getcwd(), 'Received_Reports'),
                    exist_ok=True)

        # Verify if a database already exist, if not open popup to
        # get data to start
        if not os.path.isfile(os.path.join(os.getcwd(), 'data', 'Data.json')):
            StartInfoPopup().open()

        # create a update button
        self.fb = Factory.FloatButton()
        (self.root.ids['home_screen'].ids['home']
         .add_widget(self.fb))

        # Set up list of azubis
        self.azubi_grid = \
            self.root.ids['azubi_screen'].ids['azubi_banner']
        self.newly_received_reports = \
            self.root.ids['home_screen'].ids['banner_grid']
        # Clear all data to start new if no Database exist
        try:
            # Check if there is already a Database, if so just update data
            if os.path.isfile(os.path.join(os.getcwd(), 'data', 'Data.json')):
                with open(os.path.join(os.getcwd(),
                                       'data',
                                       'Data.json'), 'r') as f:
                    data = json.load(f)
                self.check_received_reports()
                self.update_homescreen()
            # Create database
            else:
                with open(os.path.join(os.getcwd(),
                                       'data',
                                       'template.json'), 'r') as f:
                    data = json.load(f)
                with open(os.path.join(os.getcwd(), 'data', 'Data.json'), 'w',
                          encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.check_received_reports()

        except IOError:
            self.open_error_popup("Es konnte keine Datenbank erstellt werden. "
                                  "Dafür wird die Datei 'template.json' "
                                  "benötigt!")

    def check_received_reports(self, *args):
        """Update the homescreen"""
        try:
            Received_Reports = \
                sorted(listdir(os.path.join(os.getcwd(), 'Received_Reports')),
                       key=(lambda pdf: int(pdf[-6:-4]) if
                            pdf[-6].isdigit() else int(pdf[-5])))
        except (IndexError, ValueError):
            self.open_error_popup("OOPS, eine Datei im Ordner "
                                  "'./Received_Reports' gehört "
                                  "dort nicht hin. "
                                  "Bitte Dort entfernen.")
        reports = \
            [rep for rep in Received_Reports if rep not in
             self.checked_reports]
        if Received_Reports:
            for i, rep in enumerate(reports, self.counter+1):
                self.checked_reports.append(rep)
                with open(
                        os.path.join(os.getcwd(),
                                     'Received_Reports', rep), 'rb') as f:
                    pdf = PdfFileReader(f)
                    information = pdf.getDocumentInfo()
                new_report = ReportBanner(i, rep, information)
                self.newly_received_reports.add_widget(new_report)
                with open(os.path.join(os.getcwd(),
                                       'data',
                                       'Data.json'), 'r') as f:
                    data = json.load(f)
                if (information.author not in
                        data['azubis'].keys()):
                    self.update_db(information['/Email'],
                                   information.author,
                                   information['/max_num_of_rep'])
                self.counter = i

    def update_db(self, email, azubi, max_reports, *args):
        """Update the database with data from the new trainee."""
        with open(os.path.join(os.getcwd(), 'data', 'Data.json'), 'r') as f:
            data = json.load(f)
        data['azubis'][azubi] = \
            {"email": email, "max_number_of_rep": max_reports}
        with open(os.path.join(os.getcwd(),
                               'data',
                               'Data.json'), 'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def del_received_report(self, id_number, rep, *args):
        """Delete the passed report in the scroll view in the homescreen."""
        for widget in self.newly_received_reports.children:
            # Find the selected banner and delete it
            if id_number == widget.id_number:
                self.newly_received_reports.remove_widget(widget)
                if os.path.isfile(os.path.join(os.getcwd(), 'Received_Reports',
                                               rep)):
                    os.remove(os.path.join(os.getcwd(), 'Received_Reports',
                                           rep))
                    self.checked_reports.remove(rep)

    def update_azubi_list(self):
        """Update the azubiscreen."""
        with open(os.path.join(os.getcwd(), 'data', 'Data.json'), 'r') as f:
            data = json.load(f)
        self.azubi_grid.clear_widgets()
        for name in list(data['azubis'].keys()):
            if os.path.isdir(os.path.join(os.getcwd(), 'Azubis', name)):
                new_azubi = AzubiBanner(name)
                self.azubi_grid.add_widget(new_azubi)
            elif len(os.listdir(os.path.join('.', 'Received_Reports'))) == 0:
                del data['azubis'][name]
        with open(os.path.join(os.getcwd(), 'data', 'Data.json'),
                  'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_signature(self, *args):
        """Change trainee_signature in the database to True."""
        if os.path.isfile(os.path.join(os.getcwd(),
                                       'signature',
                                       'signature.png')) is True:
            subprocess.run(['python3', "TrainerSignature.py"])
        else:
            self.open_error_popup(
                "Es wurde keine Unterschrift gefunden.")

    def change_screen(self, screen_name, *args, **kwargs):
        """Change current screen to a passed screen.
        Parameters
        ----------
        screen_name : str
            The name of a screen
        """
        # get screen manager from the .kv file
        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name
        menu_text = self.root.ids['menu_txt']
        # change the menu text according to the current screen
        if screen_name in self.txt_dct:
            menu_text.text = self.txt_dct[screen_name]

    def is_filled_out(self):
        """Check if user data input is valid and completely.

        Returns
        -------
        bool
            is True if the entered data is valid else False
        """
        if (all([i != '' for i in
                [self.MY_FIRST_NAME, self.MY_LAST_NAME, self.MY_EMAIL]])):
            match = re.match(
                r'^[_a-z0-9-]+(\.[_a-z0-9-)]+)*@[a-z0-9-]+(\.[a-z]{2,4})$',
                self.MY_EMAIL)
            if match is None:
                pass
            else:
                return True
        return False

    def save_infos(self, popup=True, *args):
        """Analyze the entered user data for validity and update the user data.

        Parameters
        ----------
        popup : bool, optional
            indicates if the entered data was entered via the
            beginning popup or not (default is True)
        """
        # Check if the data is valid and completely
        if self.is_filled_out() is False:
            self.open_error_popup(
                "Die eingegebenen Daten konnten nicht übernommen werden.")
        else:
            if popup is True:
                # Change validity of database
                with open(os.path.join(os.getcwd(), 'data', 'Data.json'),
                          'r') as f:
                    data = json.load(f)
                    data['info']['valid'] = True
                with open(os.path.join(os.getcwd(), 'data', 'Data.json'),
                          'w', encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            with open(os.path.join(os.getcwd(), 'data', 'Data.json'),
                      'r') as f:
                data = json.load(f)
            data['info']['first_name'] = self.MY_FIRST_NAME
            data['info']['last_name'] = self.MY_LAST_NAME
            data['info']['my_email'] = self.MY_EMAIL
            with open(os.path.join(os.getcwd(), 'data', 'Data.json'),
                      'w', encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)


BerichtsheftApp().run()  # starts the application life cycle
