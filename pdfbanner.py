from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.app import App
from kivy.graphics import Color, Rectangle
import os.path
import webbrowser as wb
import kivy.utils


class PdfBanner(GridLayout):
    """
    Creates a banner for a PDF

    ...

    Attributes
    ----------
    btn : ScaleButton
        Initiates the dynamic class ScaleButton
    rows : int
        Number of rows in the GridLayout
    id_number : int
        To identify the PDF
    year : int
        The apprenticeship year
    c_w_number : int
        The calendar week number of the report
    azubi_name : string
        The name from the azubi
    app : App Class
        The base of the application
    rect : Rectangle
        A Class from the Kivy graphics module

    Methods
    -------
    update_rect()
        Update the position and the size of the background
    open_finalized_pdf()
        To open a selected PDF file
    """
    def __init__(self, azubi_name, id_number, year, c_w_number, **kwargs):
        super(PdfBanner, self).__init__(**kwargs)
        """
        Parameters
        ----------
        id_number : int
            To identify the PDF
        year : int
            The apprenticeship year
        c_w_number : int
            The calendar week number of the report
        azubi_name : string
            The name from the azubi
        """
        # Initiate a dynamic class from a .kv file
        self.btn = Factory.ScaleButton
        self.rows = 1
        self.id_number = id_number
        self.c_w_number = c_w_number     # calendar week number
        self.year = year
        self.app = App.get_running_app()
        self.azubi_name = azubi_name

        with self.canvas.before:
            Color(rgb=(kivy.utils.get_color_from_hex("#e4e4e4")))
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

        banner = FloatLayout()
        c_w = self.btn(text=f'  Öffne KW %d  ' % self.c_w_number,
                       bold=True,
                       background_normal='',
                       background_color=(0, 0.6, 0.2, 1),
                       size_hint=(.7, .6), font_size='27sp',
                       pos_hint={"top": .8, "x": .15})

        c_w.bind(on_press=lambda x: (self.open_finalized_pdf()))
        banner.add_widget(c_w)
        self.add_widget(banner)

    def update_rect(self, *args):
        """Update the position and the size of the background"""
        self.rect.pos = self.pos
        self.rect.size = self.size

    def open_finalized_pdf(self, *args):
        """Open selected PDF file."""
        pdf = 'Completed_Nachweis_%d.pdf' % self.id_number
        year = 'Nachweise_%d' % self.year
        path = os.path.join('.', 'Azubis', self.azubi_name, year, pdf)
        if os.path.isfile(os.path.join('.',
                                       'Azubis',
                                       self.azubi_name,
                                       year,
                                       pdf)):
            try:
                wb.get()
                wb.open_new(
                    rf"{path}")
            except Exception:
                self.app.open_error_popup("Es konnte kein ausführbarer "
                                          "Browser "
                                          "gefunden werden.")
        else:
            self.app.open_error_popup(f"PDF mit dem namen '{pdf}' "
                                      f"konnte nicht "
                                      f"im Ordner '{year}' gefunden werden.")
