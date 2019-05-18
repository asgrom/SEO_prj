#
# Меню для seo-sprint с использованием пакета urwid
#

from urwid import *
import datetime

__VERSION__ = '0.2'

search_engines = dict(
    Yandex='https://yandex.ru',
    Google='https://google.ru',
    Mail='https://mail.ru'
)

palette = [
    ('focused', 'white', 'dark blue'),
    ('btn', 'black', 'light gray'),
    ('popup', 'black', 'light gray')
]


class MyPile(Pile):

    def keypress(self, size, key):
        if key == 'enter':
            try:
                self.focus_position += 1
            except IndexError:
                self.focus_position = 0
            return
        return super().keypress(size, key)

    def mouse_event(self, size, event, btn, col, row, focus):
        return super().mouse_event(size, event, btn, col, row, focus)


def restore_widget():
    main_wgt.original_widget = main_wgt.original_widget[0]


def popup_message(message, btn_label='продолжить', callback=None):
    text_wgt = Text(message, 'center')
    if not callback:
        callback = restore_widget
    btn = button(btn_label.upper(), lambda x: callback(), size=len(btn_label) + 4)
    list_box = AttrMap(
        LineBox(
            ListBox(
                SimpleListWalker([
                    text_wgt, blank, blank, btn
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
    return Padding(
        AttrMap(
            Button(label, on_press=callback, user_data=user_data), 'btn', focus_map='focused'
        ),
        width=size, align='center'
    )


def chkbox_selected(*kargs):
    sel_chkbox, state = kargs
    if state:
        for chkbox in engine.base_widget.contents:
            if chkbox[0].base_widget is not sel_chkbox:
                chkbox[0].base_widget.set_state(False, do_callback=False)


def exit_program(key):
    if key == 'f8' or isinstance(key, Button):
        raise ExitMainLoop()


def show_visited_links():
    pass


def start_browsing():
    import time
    time.sleep(2)
    popup_message(message='Ссылка на сайт найдена')

    msg_wgt.base_widget.set_text('bla-bla-bla')


def browsing_active_page():
    _css = css_path.base_widget.edit_text
    _xpath = xpath.base_widget.edit_text
    _links_num = links_num.base_widget.edit_text

    msg_wgt.base_widget.set_text(str(datetime.datetime.now()))


blank = Divider()

timer = AttrMap(IntEdit('Таймер: '), '', focus_map='focused')

phrase = AttrMap(Edit('Фраза для поиска: '), '', focus_map='focused')

website_url = AttrMap(Edit('Адрес сайта: '), '', focus_map='focused')

geolocation = AttrMap(Edit('Местопроложение(только для Яндекса): '), '', focus_map='focused')

buttons = [
    button('ПРОСМОТР АДРЕСОВ ПОСЕЩЕННЫХ СТРАНИЦ', lambda x: show_visited_links()),
    button('НАЧАТЬ ПРОСМОТР С ПОИСКОВИКА', lambda x: start_browsing()),
    button('ВЫХОД', exit_program)
]

engine = LineBox(
    BoxAdapter(
        Filler(
            Pile([
                AttrMap(CheckBox(label, on_state_change=chkbox_selected),
                        '', focus_map='focused')
                for label in search_engines
            ]),
            top=1, bottom=1),
        height=len(search_engines) + 2),
    title='Поисковик')

msg_wgt = LineBox(
    BoxAdapter(Filler(Text(''), 'top'), height=12),
    title='Сообщения скрипта')

btns_pile = LineBox(
    BoxAdapter(
        Filler(
            Pile(buttons),
            top=1, bottom=1),
        height=len(buttons) + 2),
    title='Управление'
)

data_search_pile = LineBox(
    BoxAdapter(
        Filler(
            MyPile([timer, phrase, website_url, geolocation]),
            top=1, bottom=1),
        height=6),
    title='Данные для поиска')

cols = Columns([(30, engine), btns_pile], 1)

css_path = AttrMap(Edit('CSS-PATH элементов: '), '', focus_map='focused')
xpath = AttrWrap(Edit('XPATH элементов: '), '', focus_attr='focused')
links_num = AttrMap(IntEdit('Количество ссылок: '), '', 'focused')

active_page_wgt = LineBox(
    BoxAdapter(
        Filler(
            MyPile([css_path, xpath, links_num, timer, blank,
                    button('ПРОСМОТР ССЫЛОК НА АКТИВНОЙ СТРАНИЦЕ', browsing_active_page)]),
            top=1, bottom=1
        ),
        height=6
    ),
    title='Выбор элементов на активной странице'
)

frame = Frame(
    Padding(
        ListBox(SimpleListWalker([blank, data_search_pile, cols, active_page_wgt, msg_wgt])),
        left=2, right=2),
    header=Text('Выполнение заданий с сайтов SEOsprint, ProfitCentr', 'center'))

main_wgt = WidgetPlaceholder(
    Overlay(
        LineBox(frame),
        SolidFill('\N{MEDIUM SHADE}'),
        align='center', valign='middle',
        width=('relative', 50), height=('relative', 90),
        min_width=100, min_height=50))


def main():
    MainLoop(main_wgt, palette=palette, unhandled_input=exit_program, pop_ups=True).run()


if __name__ == '__main__':
    main()
