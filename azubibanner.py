from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.factory import Factory
import kivy.utils


class Arrow(RelativeLayout):
    def __init__(self, azubi_name, **kwargs):
        super(Arrow, self).__init__(**kwargs)
        self.azubi_name = azubi_name


class AzubiBanner(GridLayout):
    """
    Banner to optionally changing the report design

    ...

    Attributes
    ----------
    rows : int
        Number of rows in the GridLayout
    app : App Class
        The base of the application
    rect : Rectangle
        A Class from the Kivy graphics module

    Methods
    -------
    update_rect()
        Update the position and the size of the background
    """
    def __init__(self, azubi_name, **kwargs):
        super(AzubiBanner, self).__init__(**kwargs)
        """
        Parameters
        ----------
        azubi_name : string
            The name of a azubi
        """
        self.rows = 1
        self.app = App.get_running_app()
        self.azubi_name = azubi_name
        self.ScaleBtn = Factory.ScaleButton

        with self.canvas.before:
            Color(rgb=(kivy.utils.get_color_from_hex("#FFFFFF")))
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.banner = FloatLayout()
        self.azubi = self.ScaleBtn(
                            background_normal='',
                            background_down='',
                            text=self.azubi_name,
                           bold=True,
                           font_size='30sp',
                           color=(0, 0, 0, 1),
                           size_hint=(.5, .5),
                           pos_hint={"top": .75, "right": .55})
        # self.azubi.bind(size=self.azubi.setter('text_size'))
        self.backButton = Arrow(self.azubi_name)
        self.banner.add_widget(self.backButton)
        self.banner.add_widget(self.azubi)
        self.add_widget(self.banner)

    def update_rect(self, *args):
        """Update the position and the size of the background"""
        self.rect.pos = self.pos
        self.rect.size = self.size
