from colorama import init, Fore, Back, Style

init(autoreset=True)


def main_menu():
    print(Back.BLACK + f'{"":<94}')
    print(Fore.LIGHTGREEN_EX + Back.BLACK + f'{"МЕНЮ":^94}')
    print(Fore.LIGHTGREEN_EX + Back.BLACK + f'{"":-<94}')
    print(Back.BLACK + f'{"":<94}')
    print(Fore.LIGHTGREEN_EX + Back.BLACK + f'{"":<4}{"[1] ФРАЗА ДЛЯ ПОИСКА":<40}{"[5] ПОИСКОВИК":<50}')
    print(
        Fore.LIGHTGREEN_EX + Back.BLACK + f'{"":<4}{"[2] URL ВЕБ-САЙТА":<40}'
        f'{Fore.LIGHTBLUE_EX + Style.BRIGHT}{"[6] НАЧАТЬ ПРОСМОТР С ПОИСКОВИКА":<50}')
    print(
        Fore.LIGHTGREEN_EX + Back.BLACK + f'{"":<4}{"[3] МЕСТОПОЛОЖЕНИЕ (только для ЯНДЕКС)":<40}'
        f'{"[7] ПРОСМОТР ДАННЫХ ЗАПРОСА":<50}')

    print(Fore.LIGHTGREEN_EX + Back.BLACK + f'{"":<4}{"[4] ТАЙМЕР":<40}{"[8] ПРОСМОТР АДРЕСОВ ПОСЕЩЕННЫХ СТРАНИЦ":<50}')
    print(
        Back.BLACK + Fore.LIGHTGREEN_EX + f'{"":<44}'
        f'{Fore.LIGHTBLUE_EX + Style.BRIGHT}{"[9] НАЧАТЬ ПРОСМОТР ЛИНКОВ НА АКТИВНОЙ СТРАНИЦЕ":<50}')
    print(Fore.LIGHTGREEN_EX + Back.BLACK + f'{"":<4}{"[Q] ВЫХОД":<90}')
    print(Back.BLACK + f'{"":<94}')


def search_engine_menu():
    print(f'{"":<4}{"[1] Yandex"}')
    print(f'{"":<4}{"[2] Google"}')


def get_string(msg='', required=None, valid=None):
    """Получение и валидация ввода запрошенной строки"""
    msg = msg + '\n  >>>  '
    while True:
        line = input(msg)
        if not line:
            if not required:
                return ''
            else:
                print('Обязательный параметр!')
        elif valid is not None:
            if line not in valid:
                print(f'Choice one of {valid}')
            else:
                return line
        else:
            return line


def get_integer(msg='', required=None, valid=None):
    """Получение и валидация запрошенной цифровой строки"""
    msg += '\n  >>>  '
    while True:
        line = input(msg)
        if not line:
            if not required:
                return ''
            else:
                print('Обязательный параметр!')
        elif not line.isdigit():
            print('Ввести только цифры!')
        elif valid and line not in valid:
            print(f'Choise from {valid}')
        else:
            return int(line)


if __name__ == "__main__":
    main_menu()
