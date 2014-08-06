"""Sphinx Palm4fun theme.

From http://gitlab.palm4fun.com/zoom-xerus/palm4fun-sphinx-theme/repository/archive

"""
import os

VERSION = (0, 1, 0)

__version__ = ".".join(str(v) for v in VERSION)
__version_full__ = __version__


def get_html_theme_path():
    """Return list of HTML theme paths."""
    cur_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    return cur_dir