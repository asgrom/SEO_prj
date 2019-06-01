__version__ = '1.1.0'

GOOGLE = 'https://google.ru'
MAILRU = 'https://mail.ru'
YANDEX = 'https://yandex.ru'

import os

VISITED_LINKS_FILE = os.path.join(os.environ['HOME'], 'Документы/seo_visited_links')
Chrome_dir = os.path.join(os.environ["HOME"], ".local/share/seo", "chrome/profile")
Chrome_history = os.path.join(Chrome_dir, 'Default/History')

from blinker import Signal


class Signals:
    scroll = Signal()
    end = Signal()
    clicked = Signal()
    button_clicked = Signal()
