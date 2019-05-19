__version__ = '1.0.0'

GOOGLE = 'https://google.ru'
MAILRU = 'https://mail.ru'
YANDEX = 'https://yandex.ru'

from blinker import signal

progress_signal = signal('progress_signal')
scroll_done_signal = signal('scroll_done_signal')
pages_amount_signal = signal('pages_amount_signal')
all_pages_clicked_signal = signal('page_clicking_done')
