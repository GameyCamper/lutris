from gettext import gettext as _

from gi.repository import GObject, Gtk

from lutris.util import jobs
from lutris.util.jobs import schedule_repeating_at_idle
from lutris.util.log import logger


class ExtractProgressBox(Gtk.Box):
    """Progress bar used to monitor archive extraction."""

    __gsignals__ = {
        "complete": (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT,)),
        "cancel": (GObject.SignalFlags.RUN_LAST, None, ()),
        "error": (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self, archive_path: str, dest_path: str, title: str | None = None) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.archive_path = archive_path
        self.dest_path = dest_path
        self.is_complete = False
        self.cancel_requested = False

        if not title:
            title = _("Extracting %s") % archive_path

        self.main_label = Gtk.Label(label=title)
        self.main_label.set_alignment(0, 0)
        self.main_label.set_property("wrap", True)
        self.main_label.set_margin_bottom(10)
        self.pack_start(self.main_label, True, True, 0)

        progress_box = Gtk.Box()

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_margin_top(5)
        self.progressbar.set_margin_bottom(5)
        self.progressbar.set_margin_right(10)
        progress_box.pack_start(self.progressbar, True, True, 0)

        self.cancel_button = Gtk.Button.new_with_mnemonic(_("_Cancel"))
        self.cancel_button.connect("clicked", self.on_cancel_clicked)
        progress_box.pack_end(self.cancel_button, False, False, 0)

        self.pack_start(progress_box, False, False, 0)

        self.progress_label = Gtk.Label()
        self.progress_label.set_alignment(0, 0)
        self.pack_start(self.progress_label, True, True, 0)

        self.show_all()

    def start(self, extract_func) -> None:
        """Start extracting the archive."""
        self.cancel_button.set_sensitive(True)
        jobs.AsyncCall(extract_func, self.on_extract_complete, self.archive_path, self.dest_path)
        schedule_repeating_at_idle(self._progress, interval_seconds=0.1)

    def on_cancel_clicked(self, _widget=None):
        """Cancel the current extraction."""
        logger.debug("Extraction cancel requested")
        self.cancel_requested = True
        self.cancel_button.set_sensitive(False)
        self.emit("cancel")

    def _progress(self) -> bool:
        """Show extraction progress."""
        if self.cancel_requested:
            self.progressbar.set_fraction(0)
            self._set_text(_("Extraction cancelled"))
            self.emit("cancel")
            return False

        if self.is_complete:
            self.progressbar.set_fraction(1.0)
            self._set_text(_("Extraction complete"))
            self.cancel_button.set_sensitive(False)
            self.emit("complete", {})
            return False

        # Since we can't get granular progress from extract_archive, pulse the bar
        self.progressbar.pulse()
        self._set_text(_("Extracting..."))
        return True

    def on_extract_complete(self, result, error):
        """Called when extraction completes."""
        if error:
            logger.error("Extraction failed: %s", error)
            self._set_text(str(error)[:80])
            self.emit("error", error)
            return

        self.is_complete = True

    def _set_text(self, text):
        self.progress_label.set_text(text)
