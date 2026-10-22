from gettext import gettext as _

from gi.repository import Gtk

from lutris.gui.dialogs import ModalDialog
from lutris.gui.widgets.extract_progress_box import ExtractProgressBox


class ExtractDialog(ModalDialog):
    """Dialog showing extraction in progress."""

    def __init__(self, archive_path, dest_path, title=None, parent=None):
        super().__init__(title=title or _("Extracting archive"), parent=parent, border_width=10)
        self.set_size_request(485, 104)
        self.dialog_progress_box = ExtractProgressBox(
            archive_path=archive_path, dest_path=dest_path, title=_("Extracting %s") % archive_path
        )

        self.dialog_progress_box.connect("complete", self.extract_complete)
        self.dialog_progress_box.connect("cancel", self.extract_cancelled)
        self.dialog_progress_box.connect("error", self.extract_error)

        self.get_content_area().add(self.dialog_progress_box)
        self.show_all()

    def start(self, extract_func):
        """Start the extraction process."""
        self.dialog_progress_box.start(extract_func)

    def extract_complete(self, _widget, _data):
        self.response(Gtk.ResponseType.OK)

    def extract_cancelled(self, _widget):
        self.response(Gtk.ResponseType.CANCEL)

    def extract_error(self, _widget, error):
        self.response(Gtk.ResponseType.CANCEL)

    def on_response(self, dialog, response):
        if response in (Gtk.ResponseType.DELETE_EVENT, Gtk.ResponseType.CANCEL):
            pass  # Extraction is already handled by the progress box
        super().on_response(dialog, response)
