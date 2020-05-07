from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.core.window import Window
import os
from kivy.garden.navigationdrawer import NavigationDrawer as ND


class NavDemoWindow(ND):
    pass


class HomeScreen(Screen):
    pass


class AzubiScreen(Screen):
    """
    Shows every azubi in a list
    """
    pass


class OverviewScreen(Screen):
    """
    Informations from a specific azubi
    """
    pass


class FinalizedBannerScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class InfoScreen(Screen):
    pass


class SignatureScreen(Screen):
    """
    Screen to get the signature from the user.

    ...

    Attributes
    ----------
    drawing : ObjectProperty
        A reference to the widget Pencil from within a .kv file
        from our python script
    foreground_red : int
        Used as the first number in a RGB color code
    foreground_green : int
        Used as the second number in a RGB color code
    foreground_blue : int
        Used as the third number in a RGB color code
    linewidth : int
        The thickness of the lines drawn

    Methods
    -------
    clear_sig
        Clear all drawings on the screen.
    save_sig
        Save the signature in the CWD as a PNG.
    give_black
        Change color to black.
    give_blue
        Change color to blue.
    set_width_5
        Set the width of the lines to 3.
    """
    drawing = ObjectProperty(None)
    foreground_red = 0
    foreground_green = 0
    foreground_blue = 0
    linewidth = 3
    db_path = os.path.join(os.getcwd(), 'data', 'Bh_data.json')

    def clear_sig(self, *args):
        """Clear all drawings on the screen."""
        self.drawing.canvas.clear()

    def save_sig(self, *args):
        """Save the signature in the CWD as a PNG."""
        self.drawing.size = (Window.size[0], Window.size[1])
        project_path = os.getcwd()
        build_path = os.path.join(project_path, 'signature')
        os.makedirs(build_path, exist_ok=True)
        path = os.path.join(build_path, 'signature.png')
        self.drawing.export_to_png(path)

    # colour button
    def give_black(self, *args):
        """Change color to black."""
        self.foreground_red = 0
        self.foreground_green = 0
        self.foreground_blue = 0

    def give_blue(self, *args):
        """Change color to blue."""
        self.foreground_red = 0
        self.foreground_green = 0
        self.foreground_blue = 1

    def set_width_5(self, *args):
        """Set the width of the lines to 5."""
        self.linewidth = 3