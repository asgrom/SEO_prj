"""Модуль меню с использованием библиотеки 'urwid'

Данные для поиска вводятся в соотвествующие поля ввода в меню. При вводе в поля данные автоматичести вносятся в словари.
Есть два словаря:
        data_for_request - словарь содержит основные данные поиска.
                        URL веб-сайта. Местоположение (для поисковика Яндекс).
                        Адрес нужного поисковика.
                        Фразу, по которой будет происходить поиск.
                        Время, на которое нужно задержать на странице.
        selectors_for_links - словарь содержит xpath, css элементов страницы, которые нужно найти.
                        Количество необходимых элементов.

При нажатии на кнопку <ПОИСК ЗАДАННОГО САЙТ> запускается браузер, запускается страница выбранной поисковой системы.
Если поисковая система - Яндекс и если задано местоположение, то оно задается на странице выбора местоположения. В поле
поиска на странице вводится поисковая фраза и запускается поиск. Если ссылка на необходимый сайт будет найдена, то в
программе появится окно с сообщением, что сайт найден. При нажатии на кнопку <ПРОДОЛЖИТЬ> произойдет переход на сайт.

Далее в программе нужно задать критерии (css или xpath) элементов, по которым будут осуществлятся переходы. Необходимо
задать таймер, а также необходимое количество элементов. Поиск элементов и переход по ним начинается после нажатия
кнопки <ПРОСМОТР ССЫЛОК НА АКТИВНОЙ СТРАНИЦЕ>.

Ход выполнения переходов и прокрутки страниц отображается в прогресс-барах.

При запущенном браузере при нажатии на кнопку <ПРОСМОТР ССЫЛОК НА АКТИВНОЙ СТРАНИЦЕ> последняя вкладка делается
активной и поиск будет происходить на ней.

Все ошибки программы отображаются в соответствующем виджете.
"""

from blinker import signal
from urwid import *
from urwid_timed_progress import TimedProgressBar

from seo import seo_urwid

__VERSION__ = '0.2'

search_engines = dict(
    Yandex='https://yandex.ru',
    Google='https://google.ru',
    Mail='https://mail.ru'
)

palette = [
    ('focused', 'white', 'dark blue'),
    ('btn', 'black', 'light gray'),
    ('popup', 'black', 'light gray'),
    ('important', 'light red,bold', ''),
    ('normal', 'white', 'black'),
    ('complete', 'white', 'dark magenta')
]

ChromeDrv = None

class MyPile(Pile):
    """Обычной класс Pile

    Перегружен метод обработки нажатий клавиатуры.
    При нажатии <ENTER> фокус переходит на следующий элемет, содержащийся в стопке Pile"""

    def keypress(self, size, key):
        if key == 'enter':
            try:
                self.focus_position += 1
            except IndexError:
                self.focus_position = 0
            return
        return super().keypress(size, key)


def restore_widget():
    """Восстанавливает предыдущий вид основного виджета"""

    main_wgt.original_widget = main_wgt.original_widget[0]


def print_msg(obj):
    """Выводит текст в виджете сообщений в меню"""

    msg_wgt.base_widget.set_text(str(obj))


def popup_message(message, btn_label='продолжить', callback=None):
    """Всплывающий виджет

    Создается виджет Overlay и им заменяется оригинальный виджет (original_widget) основного (WidgetPlaceHolder)
    виджета меню
    """

    text_wgt = Text(message, 'center')
    btn = button(btn_label.upper(), size=len(btn_label) + 4)

    connect_signal(btn.base_widget, 'click', lambda x: restore_widget())
    if callback is not None:
        connect_signal(btn.base_widget, 'click', lambda x: callback())

    list_box = AttrMap(
        LineBox(
            ListBox(
                SimpleListWalker([
                    text_wgt, blank, btn
                ])
            )
        ), 'popup'
    )

    main_wgt.original_widget = Overlay(
        list_box, main_wgt.original_widget,
        align='center', valign=('relative', 30),
        width=40, height=7
    )


def button(label, callback=None, user_data=None, size=40):
    """Создает виджет кнопки"""
    return Padding(
        AttrMap(
            Button(label.upper(), on_press=callback, user_data=user_data), 'btn', focus_map='focused'
        ),
        width=size, align='center'
    )


def chkbox_selected(*kargs):
    """Проверяет статусы чекбоксов

    При выборе чекбокса проверяет статусы остальных чекбоксов. Изменяет их статусы на False.
    При изменении статусов не генерируется сигнал об их изменении.
    """
    sel_chkbox, state = kargs
    seo_urwid.data_for_request['search_engine'] = search_engines[sel_chkbox.label]
    if state:
        for chkbox in engine.base_widget.contents:
            if chkbox[0].base_widget is not sel_chkbox:
                chkbox[0].base_widget.set_state(False, do_callback=False)


def exit_program(key):
    if key == 'f8' or isinstance(key, Button):
        try:
            seo_urwid.exit_prog()
        except Exception as e:
            print_msg(e)
        raise ExitMainLoop()


def start_browsing():
    """Запускает браузер

    Запускается браузер. Происходит поиск ссылки на сайт в поисковике. Если ссылка найдена, появляется сообщение об этом
    """
    global ChromeDrv
    try:
        seo_urwid.browser_init()
        seo_urwid.find_website_link()
        popup_message('Ссылка на сайт найдена\nНажми кнопку для перехода на сайт', callback=continue_browsing)
    except Exception as e:
        print_msg(e)


def browsing_active_page():
    """Поиск элементов на активной вкладке браузера"""
    try:
        seo_urwid.start_links_click()
    except Exception as e:
        print_msg(e)
    finally:
        seo_urwid.write_visited_links(mode='a')


def continue_browsing():
    """Переход на найденный сайт

    Функция запускается после нажатия на кнопку в сообщении о том, что ссылка на сайт найдена.
    """
    try:
        seo_urwid.continue_browsing()
    except Exception as e:
        print_msg(e)
    finally:
        seo_urwid.write_visited_links(mode='w')


def change_data_for_request(obj, text, key):
    """Изменяет данные с ключем key в словаре с данными для поиска

    Функция запускается при изменении полей ввода и вносит изменения в словарь с данными."""
    if key == 'timer':
        seo_urwid.data_for_request[key] = int(text) if len(text) != 0 else None
    else:
        seo_urwid.data_for_request[key] = text.lower()


def change_selectors_for_links(obj, text, key):
    """Изменяет словать с селекторами элементов

    Запускается при изменении полей ввода селекторов элементов страницы"""
    if key == 'num_links_to_click':
        seo_urwid.selectors_for_links[key] = int(text) if len(text) != 0 else None
    else:
        seo_urwid.selectors_for_links[key] = text.lower()


def attr_wrap(obj):
    """Оборачивает элемент в атрибут"""
    return AttrMap(obj, '', focus_map='focused')


# сигналы посылаютя экземпляром Browser
scroll = signal('scroll')  # сигнал посылает экземпляр класса Brouser при прокрутке страницы
scroll_end = signal('scroll-end')  # сигнал окончания прокрутки страницы


@scroll.connect_via('scroll')
def update_page_scroll_bar(sender, done):
    page_scroll_bar.add_progress(1, done=done)
    loop.draw_screen()


@scroll_end.connect
def reset_page_scroll_bar(sender):
    page_scroll_bar.reset()
    loop.draw_screen()


# эти два сигнала посылаются из модуля seo_urwid при кликах на ссылках
link_clicked = signal('link-clicked')  # сигнал посылается при переходе по ссылке
loop_end = signal('loop-end')  # сигнал посылается после посещения всех ссылок


@link_clicked.connect
def update_page_amount_bar(sender, done):
    page_amount_bar.add_progress(1, done=done)
    loop.draw_screen()


@loop_end.connect
def reset_page_amount_bar(sender):
    page_amount_bar.reset()
    loop.draw_screen()


blank = Divider()

timer = AttrMap(IntEdit('Таймер: '), '', focus_map='focused')

phrase = AttrMap(Edit('Фраза для поиска: '), '', focus_map='focused')

website_url = AttrMap(Edit('Адрес сайта: '), '', focus_map='focused')

geolocation = AttrMap(Edit('Местопроложение(только для Яндекса): '), '', focus_map='focused')

css_path = AttrMap(Edit('CSS-PATH элементов: '), '', focus_map='focused')

xpath = AttrWrap(Edit('XPATH элементов: '), '', focus_attr='focused')

links_num = AttrMap(IntEdit('Количество ссылок: '), '', 'focused')

buttons = [
    button('ПРОСМОТР АДРЕСОВ ПОСЕЩЕННЫХ СТРАНИЦ', lambda x: seo_urwid.print_visited_links()),
    button('поиск заданного сайта', lambda x: start_browsing()),
    button('ВЫХОД', exit_program)
]

engine = AttrMap(
    LineBox(
        Padding(
            Pile([
                *[attr_wrap(CheckBox(label, on_state_change=chkbox_selected))
                  for label in search_engines],
            ]), left=1, right=1
        ), title='ПОИСКОВИК', title_attr='important'
    ), 'important')

msg_wgt = LineBox(
    BoxAdapter(Filler(Text(''), 'top'), height=12),
    title='Сообщения скрипта')

btns_pile = LineBox(
    Pile([*buttons]), title='Управление'
)

data_search_pile = LineBox(
    Padding(
        Pile(
            [phrase, website_url, geolocation]
        ), left=1, right=1
    ), title='Данные для поиска'
)

cols = Columns([(30, engine), btns_pile], 1)

##################################################################################################
# Signals                                                                                       ##
##################################################################################################

connect_signal(timer.base_widget, 'change', change_data_for_request, user_arg='timer')
connect_signal(phrase.base_widget, 'change', change_data_for_request, user_arg='phrase')
connect_signal(website_url.base_widget, 'change', change_data_for_request, user_arg='website_url')
connect_signal(geolocation.base_widget, 'change', change_data_for_request, user_arg='geo_location')

connect_signal(css_path.base_widget, 'change', change_selectors_for_links, 'css_elems')
connect_signal(xpath.base_widget, 'change', change_selectors_for_links, 'xpath_elems')
connect_signal(links_num.base_widget, 'change', change_selectors_for_links, 'num_links_to_click')
##################################################################################################


page_amount_bar = TimedProgressBar('normal', 'complete', units='Page', label='Страницы')
page_scroll_bar = TimedProgressBar('normal', 'complete', units='Click', label='Прокрутка')

progress_bar_wgt = LineBox(
    Padding(
        Pile(
            [blank, page_scroll_bar, page_amount_bar]
        ), left=1, right=1),
    title='Прогресс кликов и прокрутки страниц'
)

selectors_wgt = LineBox(
    Padding(
        MyPile([css_path, xpath, links_num, timer,
                button('ПРОСМОТР ССЫЛОК НА АКТИВНОЙ СТРАНИЦЕ', lambda x: browsing_active_page())]),
        left=1, right=1),
    title='Выбор элементов на активной странице')

frame = Frame(
    Padding(
        ListBox(SimpleListWalker([blank, data_search_pile, cols, selectors_wgt, progress_bar_wgt, msg_wgt])),
        left=2, right=2),
    header=Text('Выполнение заданий с сайтов SEOsprint, ProfitCentr', 'center'))

main_wgt = WidgetPlaceholder(
    Overlay(
        LineBox(frame),
        SolidFill('\N{MEDIUM SHADE}'),
        align='center', valign='middle',
        width=('relative', 50), height=('relative', 90),
        min_width=100, min_height=50))

loop = MainLoop(main_wgt, palette=palette, unhandled_input=exit_program, handle_mouse=False)


def main():
    loop.run()


if __name__ == '__main__':
    main()
