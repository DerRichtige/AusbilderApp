from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.modalview import ModalView
from kivy.factory import Factory
import kivy.utils
import json
import smtplib
from email.message import EmailMessage
import re
import os
import os.path
import webbrowser as wb
from PyPDF2 import PdfFileReader, PdfFileWriter


class ImgButton(ButtonBehavior, Image):
    pass


class RejectEmail(ModalView):
    """
    Popup to ask for password and to send it

    ...

    Attributes
    ----------
    id_number : int
        To identify the report
    year : int
        The apprenticeship year
    app : App class
        The base of the application
    name : string
        The name of the azubi
    trainee_email : string
        The trainee's email address
    report_name : string
        The name of the PDF file
    report_number : string
        The header of the report

    Methods
    -------
    send_rejection_email(pw, explanatory_text)
        Sends e-mail using the SMTP-protocol
    """
    def __init__(self, name, year,
                 id_number,
                 report_number,
                 rep,
                 email,
                 **kwargs):
        super(RejectEmail, self).__init__(**kwargs)
        """
        Parameters
        ----------
        id_number : int
            To identify the report
        year : int
            The apprenticeship year
        name : string
            The name of the azubi
        email : string
            The trainee's email address
        rep : string
            The name of the PDF file
        report_number : string
            The header of the report
        """
        self.year = year
        self.name = name
        self.id_number = id_number
        self.report_number = report_number.split('_')[1]
        self.trainee_email = email
        self.report_name = rep
        self.app = App.get_running_app()

    def send_rejection_email(self, pw, explanatory_text, *args):
        """sends a rejection e-mail using the SMTP-protocol.

        Parameters
        ----------
        pw : string
            The password of the trainees email address
        explanatory_text : string
            The declaration of rejection
        """
        # Details of Outgoing servers from some providers
        servers = {"gmail": ["smtp.gmail.com", 465],
                   "gmx": ["mail.gmx.net", 465],
                   "yahoo": ["smtp.mail.yahoo.com", 465],
                   "t-online": ["securesmtp.t-online.de", 465],
                   "1und1": ["smtp.1und1.de", 465],
                   "freenet": ["mx.freenet.de", 465],
                   "aol.com": ["smtp.de.aol.com", 465],
                   "aim": ["smtp.aim.com", 465],
                   "aol.de": ["smtp.aim.com", 465],
                   "arcor": ["mail.arcor.de", 465],
                   "eclipso": ['mail.eclipso.de', 465],
                   "firemail": ['firemail.de', 465],
                   "me": ['smtp.mail.me.com', 465],
                   "mail": ['smtp.mail.de', 465],
                   "mailbox": ['smtp.mailbox.org', 465],
                   "smart-mail": ['smtp.smart-mail.de', 465],
                   "outlook": ['smtp-mail.outlook.com', 587],
                   "netcologne": ['smtp.netcologne.de', 587],
                   "o2online": ['smtp.o2online.de', 587],
                   "web": ["smtp.web.de", 587],
                   "vodafone": ['smtp.vodafonemail.de', 587]}

        with open(os.path.join(os.getcwd(), 'data',
                               'Data.json'), 'r') as f:
            data = json.load(f)
        # The SMTP-protocol has to be activated by the e-mail provider
        EMAIL_ADDR = data['info']['my_email']
        EMAIL_PW = pw
        SERVER = ''
        PORT = ''
        pattern = re.compile(
            (r'(?<=[@|\.])(gmx|mail|1und1|freenet|vodafone|aim'
             r'|gmail|t-online|web|yahoo|outlook|aol|arcor|'
             r'|o2online|netcologne|smart-mail|mailbox|firemail|eclipso|me)'),
            re.I)
        try:
            match = pattern.search(EMAIL_ADDR)
            # get the right SERVER and PORT for the specific e-mail
            if match.group(0) in servers:
                SERVER, PORT = servers[match.group(1)]
            # create e-mail
            msg = EmailMessage()
            msg['Subject'] = (f'Nachweis Nr. {self.report_number} - ABGELEHNT '
                              f'- Lehrjahr: {self.year}')
            msg['From'] = EMAIL_ADDR
            msg['To'] = self.trainee_email
            msg.set_content(f"Nachweis Nr. {self.report_number} "
                            f"wurde ABGELEHNT.\n\n{explanatory_text}")

            # Use smtplib client to communicate with a remote SMTP server from
            # a specific provider
            try:
                # try to login and send data
                with smtplib.SMTP_SSL(host=SERVER, port=PORT) as server:
                    server.login(EMAIL_ADDR, EMAIL_PW)
                    server.send_message(msg)
                self.app.del_received_report(self.id_number,
                                             self.report_name)
            except smtplib.SMTPAuthenticationError:
                error = ("Bitte überprüfen Sie ihre E-Mail-Adresse und Ihr "
                         "dazu gehöriges Passwort bzw. sorgen Sie dafür, "
                         "dass bei ihrem E-Mail Provider das SMTP-Protokoll "
                         "nicht deaktiviert ist")
                self.app.open_error_popup(error)
        except Exception:
            error = "Der Provider Ihrer E-Mail-Adresse wird nicht unterstützt"
            self.app.open_error_popup(error)


class AcceptEmail(ModalView):
    """
    Popup to ask for password and to send it

    ...

    Attributes
    ----------
    id_number : int
        To identify the report
    year : int
        The apprenticeship year
    app : App Class
        The base of the application
    name : string
        The name of the azubi
    email : string
        The trainee's email address
    report_name : string
        The name of the PDF file
    report_number : string
        The header of the report

    Methods
    -------
    send_acceptance_email(pw)
        Sends an accepted e-mail using the SMTP-protocol.
    """
    def __init__(self, id_number, report_number,
                 year, name, report_name, email, **kwargs):
        super(AcceptEmail, self).__init__(**kwargs)
        """
        Parameters
        ----------
        id_number : int
            To identify the report
        year : int
            The apprenticeship year
        name : string
            The name of the azubi
        email : string
            The trainee's email address
        report_name : string
            The name of the PDF file
        report_number : string
            The header of the report
        """
        self.id_number = id_number
        self.report_number = report_number
        self.year = year
        self.name = name
        self.report_name = report_name
        self.trainee_email = email

    def put_signature(self, *args):
        if os.path.isdir(os.path.join('.', 'Azubis')):
            pass
        else:
            os.mkdir(os.path.join('.', 'Azubis'))

        if os.path.isdir(os.path.join('.', 'Azubis', self.name)):
            pass
        else:
            os.mkdir(
                os.path.join('.', 'Azubis', self.name))
            os.mkdir(
                os.path.join('.', 'Azubis', self.name,
                             'Nachweise_1'))
            os.mkdir(
                os.path.join('.', 'Azubis', self.name,
                             'Nachweise_2'))
            os.mkdir(
                os.path.join('.', 'Azubis', self.name,
                             'Nachweise_3'))

        file1 = \
            open(os.path.join('.', 'Template', 'trainer_signature.pdf'), "rb")
        file2 = \
            open(os.path.join('.', 'Received_Reports', self.report_name), "rb")
        f1 = PdfFileReader(file1)
        f2 = PdfFileReader(file2)
        metadata = f2.getDocumentInfo()
        output = PdfFileWriter()
        page = f1.getPage(0)
        page.mergePage(f2.getPage(0))
        output.addPage(page)
        output.addMetadata(metadata)
        outputStream = \
            open(os.path.join('.', 'Azubis', self.name,
                              f"Nachweise_{str(self.year)}",
                              f'Completed_{self.report_number}'), "wb")
        output.write(outputStream)
        outputStream.close()
        os.rename(os.path.join('.', 'Azubis', self.name,
                               f"Nachweise_{str(self.year)}",
                               f'Completed_{self.report_number}'),
                  os.path.join('.', 'Azubis', self.name,
                               f"Nachweise_{str(self.year)}",
                  f'Completed_{self.report_number}'+'.pdf'))
        file1.close()
        file2.close()

    def send_acceptance_email(self, pw, *args):
        """sends an accepted e-mail using the SMTP-protocol."""
        # Details of Outgoing servers from some providers
        servers = {"gmail": ["smtp.gmail.com", 465],
                   "gmx": ["mail.gmx.net", 465],
                   "yahoo": ["smtp.mail.yahoo.com", 465],
                   "t-online": ["securesmtp.t-online.de", 465],
                   "1und1": ["smtp.1und1.de", 465],
                   "freenet": ["mx.freenet.de", 465],
                   "aol.com": ["smtp.de.aol.com", 465],
                   "aim": ["smtp.aim.com", 465],
                   "aol.de": ["smtp.aim.com", 465],
                   "arcor": ["mail.arcor.de", 465],
                   "eclipso": ['mail.eclipso.de', 465],
                   "firemail": ['firemail.de', 465],
                   "me": ['smtp.mail.me.com', 465],
                   "mail": ['smtp.mail.de', 465],
                   "mailbox": ['smtp.mailbox.org', 465],
                   "smart-mail": ['smtp.smart-mail.de', 465],
                   "outlook": ['smtp-mail.outlook.com', 587],
                   "netcologne": ['smtp.netcologne.de', 587],
                   "o2online": ['smtp.o2online.de', 587],
                   "web": ["smtp.web.de", 587],
                   "vodafone": ['smtp.vodafonemail.de', 587]}

        with open(os.path.join(os.getcwd(), 'data',
                               'Data.json'), 'r') as f:
            data = json.load(f)

        # The SMTP-protocol has to be activated by the e-mail provider
        EMAIL_ADDR = data['info']['my_email']
        EMAIL_PW = pw
        SERVER = ''
        PORT = ''
        pattern = re.compile(
            (r'(?<=[@|\.])(gmx|mail|1und1|freenet|vodafone|aim'
             r'|gmail|t-online|web|yahoo|outlook|aol|arcor|'
             r'|o2online|netcologne|smart-mail|mailbox|firemail|eclipso|me)'),
            re.I)
        match = pattern.search(EMAIL_ADDR)
        try:
            # get the right SERVER and PORT for the specific e-mail
            if match.group(0) in servers:
                SERVER, PORT = servers[match.group(1)]
            # create e-mail
            msg = EmailMessage()
            msg['Subject'] = ("Nachweis Nr. "
                              f"{self.report_number.split('_')[1]} -"
                              f" Lehrjahr: {self.year}")
            msg['From'] = EMAIL_ADDR
            msg['To'] = self.trainee_email

            msg.set_content(f"Sehr geehrte(r) Herr/Frau {self.name}, "
                            "\n\nihr gesendeter Nachweis Nr. "
                            f"{self.report_number.split('_')[1]} "
                            "wurde akzeptiert\n\nFreundliche Grüße "
                            f"\n{data['info']['first_name']} "
                            f"{data['info']['last_name']}"
                            "\n\n***Bitte speichern Sie die PDF im Dateipfad, "
                            "wo sich Ihre Berichtsheft-APP befindet, "
                            "im Ordner "
                            f"{'Berichtsheft_Fertig_%d' % self.year}."
                            " Also standard mäßig im Dateipfad  ~/BerichtsHeft"
                            f"_APP/{'Berichtsheft_Fertig_%d' % self.year}***")

            # e-mail attachment
            self.put_signature()
            attachment = \
                os.path.join('.',
                             'Azubis',
                             self.name,
                             f"Nachweise_{str(self.year)}",
                             f'Completed_{self.report_number}.pdf')
            with open(attachment, 'rb') as f:
                file_data = f.read()
            # Add attachment to e-mail
            msg.add_attachment(file_data,
                               maintype='application',
                               subtype='octet-stream',
                               filename=(f'{self.report_number}.pdf'))

            # Use smtplib client to communicate with a remote SMTP server
            # from a specific provider
            try:
                # try to login and send data
                with smtplib.SMTP_SSL(host=SERVER, port=PORT) as server:
                    server.login(EMAIL_ADDR, EMAIL_PW)
                    server.send_message(msg)
                App.get_running_app().del_received_report(self.id_number,
                                                          self.report_name)
            except smtplib.SMTPAuthenticationError:
                error = ("Bitte überprüfen Sie ihre E-Mail-Adresse und Ihr "
                         "dazu gehöriges Passwort bzw. sorgen Sie dafür, "
                         "dass bei ihrem E-Mail Provider das "
                         "SMTP-Protokoll nicht deaktiviert ist")
                App.get_running_app().open_error_popup(error)
        except Exception:
            error = "Der Provider Ihrer E-Mail-Adresse wird nicht unterstützt"
            App.get_running_app().open_error_popup(error)


class ReportBanner(GridLayout):
    """
    Banner for a report from a specific calendar week in a year.

    ...

    Attributes
    ----------
    rows : int
        Number of rows in the GridLayout
    f_name : string
        The first name of the trainee
    l_name : string
        The last name of the trainee
    trainee_email : string
        The trainee's e-mail address
    year : int
        The apprenticeship year
    id_number : int
        To identify the report
    report_name : string
        The name of the PDF
    app : App class
        The base of the application
    rect : Rectangle
        A class from the Kivy graphics module
    scaleBtn : ScaleButton object
        A button which scales with the screen size
    scaleLbl : ScaleLabel object
        A Label which scales with the screen size
    period : string
        The date from monday to the next friday of the specific
        calendar week
    name : string
        The name of the trainee
    cal_w : string
        The calendar week

    Methods
    -------
    update_rect()
        Update the position and the size of the background.
    accept_report()
        Ask to enter the e-mail password to send a acception message.
    def reject_report(self):
        Ask to enter the e-mail password to send a rejection message.
    open_finalized_pdf()
        Open selected PDF file.
    """
    def __init__(self, id_number, report_name, information, **kwargs):
        super(ReportBanner, self).__init__(**kwargs)
        """
        Parameters
        ----------
        id_number : int
            To identify the PDF
        report_name : string
            The name of the file
        information : pdf.getDocumentInfo()
            The metadata from the PDF file
        """
        self.rows = 1
        self.scaleBtn = Factory.ScaleButton
        self.scaleLbl = Factory.ScaleLabel
        self.f_name, self.l_name = information.author.split(' ')
        self.id_number = id_number
        self.report_name = report_name
        self.year = int(information['/Apprenticeship_year'])
        self.trainee_email = information['/Email']
        self.app = App.get_running_app()
        self.report_number = information['/Filename']
        period = information['/Period']
        name = f'{self.f_name} {self.l_name[0]}.'
        cal_w = information['/Calendar_week']

        with self.canvas.before:
            Color(rgb=(kivy.utils.get_color_from_hex("#FFFFFF")))
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

        banner = BoxLayout(orientation='vertical')
        bottom_bar = BoxLayout(orientation='horizontal', size_hint=(1, .3))

        infos = self.scaleBtn(text=(f"        [color=FFFFFF]{name}[/color]"
                                    f"     | {self.year}. Ausbildungsjahr | "
                                    f"{period}   "),
                              color=(1, 1, 1, 1),
                              size_hint=(1, 1),
                              font_size='14sp',
                              bold=True,
                              markup=True,
                              background_normal='',
                              background_color=(.47, .62, .8, 1),
                              background_down='')
        bottom_bar.add_widget(infos)
        # The left side
        top_bar = BoxLayout(orientation='horizontal')
        banner_left = BoxLayout(size_hint_x=(.5))
        calendar_week = self.scaleBtn(text='KW %d' % int(cal_w),
                                      color=(0, .6, .2, 1),
                                      bold=True, size_hint=(1, .6),
                                      font_size='1cm',
                                      pos_hint={"top": .8, "right": 1},
                                      background_normal='',
                                      background_down='')
        banner_left.add_widget(calendar_week)
        # THe right side
        banner_right = BoxLayout(padding=[30, 0, 30, 0], spacing=10)
        show_pdf_button = \
            ImgButton(source=os.path.join('.', 'icons', 'PDF_symbol.png'),
                      size_hint=(1, .6),
                      pos_hint={"top": .8})
        show_pdf_button.bind(on_press=lambda x: (self.open_finalized_pdf()))
        decline_email_button = \
            ImgButton(source=os.path.join('.', 'icons', 'reject_rep.png'),
                      size_hint=(1, .6),
                      pos_hint={"top": .8})
        decline_email_button.bind(on_press=lambda x: (self.reject_report()))
        accept_email_button = \
            ImgButton(source=os.path.join('.', 'icons', 'accepted.png'),
                      size_hint=(1, .6),
                      pos_hint={"top": .8})
        accept_email_button.bind(on_press=lambda x: (self.accept_report()))

        banner_right.add_widget(show_pdf_button)
        banner_right.add_widget(accept_email_button)
        banner_right.add_widget(decline_email_button)

        top_bar.add_widget(banner_left)
        top_bar.add_widget(banner_right)

        banner.add_widget(top_bar)
        banner.add_widget(bottom_bar)
        self.add_widget(banner)

    def update_rect(self, *args):
        """Update the position and the size of the background."""
        self.rect.pos = self.pos
        self.rect.size = self.size

    def reject_report(self):
        """Ask to enter the e-mail password to send a rejection message."""
        if os.path.isfile(os.path.join(os.getcwd(),
                                       'signature',
                                       'signature.png')) is True:
            RejectEmail(f"{self.f_name} {self.l_name}",
                        self.year,
                        self.id_number,
                        self.report_number,
                        self.report_name,
                        self.trainee_email).open()
        else:
            self.app.open_error_popup('Keine Unterschrift wurde gefunden. '
                                      '\nBitte erstellen Sie eine in der App.')

    def accept_report(self):
        """Ask to enter the e-mail password to send a acception message."""
        if os.path.isfile(os.path.join(os.getcwd(),
                                       'signature',
                                       'signature.png')) is True:
            AcceptEmail(self.id_number,
                        self.report_number,
                        self.year,
                        f"{self.f_name} {self.l_name}",
                        self.report_name,
                        self.trainee_email).open()
        else:
            self.app.open_error_popup('Keine Unterschrift wurde gefunden. '
                                      '\nBitte erstellen Sie eine in der App.')

    def open_finalized_pdf(self, *args):
        """Open selected PDF file."""
        path = os.path.join('.', 'Received_Reports', self.report_name)
        if os.path.isfile(os.path.join('.',
                                       'Received_Reports',
                                       self.report_name)):
            try:
                wb.get()
                wb.open_new(
                    rf"{path}")
            except Exception:
                self.app.open_error_popup("Es konnte kein ausführbarer "
                                          "Browser "
                                          "gefunden werden.")
        else:
            self.app.open_error_popup(f"PDF mit dem namen '{self.report_name}'"
                                      " konnte nicht im Ordner "
                                      "'Received_Reports' gefunden werden.")
