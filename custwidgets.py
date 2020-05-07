from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, StringProperty
from kivy.graphics import Line, Color
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import ButtonBehavior
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from CheckEmails import CheckEmailsPopup
import re


class ImageButton(ButtonBehavior, Image):
    pass


class ErrorPopup(ModalView):
    """
    Popup with a specific error message

    ...

    Attributes
    ----------
    error_message : StringProperty
        Error message text and is a Kivy property to update the error message
    """
    error_message = StringProperty('')

    def __init__(self, error_message, **kwargs):
        super(ErrorPopup, self).__init__(**kwargs)
        self.error_message = error_message


class StartInfoPopup(ModalView):
    pass


class MyLabel(Image):
    """
    Scales the text header correctly to match given size

    ...

    Attributes
    ----------
    text : StringProperty
        Header text and to update the text its a Kivy property

    Methods
    -------
    on_text(*_)
        Scale final texture of a large font size to match given size
    """

    text = StringProperty('')

    def on_text(self, *_):
        """Scale the header text."""
        # Just get large texture:
        lbl = Label(text=self.text)
        lbl.font_size = '1000sp'
        lbl.font_name = 'Roboto-Bold'
        lbl.outline_width = 50
        lbl.padding_x = 250
        lbl.texture_update()
        # Set it to image, it'll be scaled to image size automatically:
        self.texture = lbl.texture


class NumberInput(TextInput):
    """
    Text input which only accept numbers

    ...

    Methods
    -------
    insert_text
        Replace each entered letter with a number.
    update_padding
        Centers every input.
    """
    def insert_text(self, substring, from_undo=False):
        """Replace each entered letter with a number."""
        pat = re.compile('[^0-9]')
        # substring = substring[:2 - len(self.text)]
        s = re.sub(pat, '', substring)
        return super(NumberInput, self).insert_text(s, from_undo=from_undo)

    def update_padding(self, *args):
        """Centers every input."""
        self.text_width = self._get_text_width(self.text,
                                               self.tab_width,
                                               self._label_cached)
        self.padding = [(self.width - self.text_width) / 2,
                        (self.height / 2.0 -
                            (self.line_height / 2.0) * len(self._lines)),
                        0,
                        0]


class Pencil(Widget):
    """
    Class that uses the widget's canvas object to draw into the window

    ...

    Attributes
    ----------

    sig_screen : ObjectProperty
        A reference to the widget SignatureScreen from within a
        .kv file from our python script

    Methods
    -------
    on_touch_down
        Create a new line for every new touch event.
    on_touch-move
        Update the line when the touch has moved.
    """
    sig_screen = ObjectProperty()

    # This method is being called when a new touch occurs.
    def on_touch_down(self, touch):
        """Create a new line for every new touch event.

        Parameters
        ----------
        touch : MotionEvent (and provides the events on_touch_XXX)
            Used to store custom attributes for a touch
        """
        with self.canvas:
            Color(self.sig_screen.foreground_red,
                  self.sig_screen.foreground_green,
                  self.sig_screen.foreground_blue,
                  0.8)
            # store a reference to a line object in a dictionary
            touch.ud["line1"] = Line(points=(touch.x, touch.y),
                                     width=self.sig_screen.linewidth)

    # This method is being called when an existing touch moves.
    def on_touch_move(self, touch):
        """Update the line when the touch has moved.

        Parameters
        ----------
        touch : MotionEvent (and provides the events on_touch_XXX)
            Used to get access to the same MotionEvent object with
            updated attributes
        """
        # get access to the line that is set up for this touch earlier
        if 'line1' in touch.ud:
            # add the current position of the touch as a new point
            touch.ud["line1"].points += [touch.x, touch.y]
