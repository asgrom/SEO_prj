__version__ = '1.1.0'

GOOGLE = 'https://google.ru'
MAILRU = 'https://mail.ru'
YANDEX = 'https://yandex.ru'

import os

VISITED_LINKS_FILE = os.path.join(os.environ['HOME'], 'Документы/seo_visited_links')

from blinker import Signal


class Signals:
    scroll = Signal()
    end = Signal()
    clicked = Signal()
    button_clicked = Signal()
