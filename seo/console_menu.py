from colorama import init, Fore, Style, Back

init(autoreset=True)


def main_menu():
    print(Back.BLACK + f'{"":<80}')
    print(Fore.LIGHTGREEN_EX + Back.BLACK + f'{"Меню":^80}')
    print(Fore.LIGHTGREEN_EX + Back.BLACK + f'{"":-<80}')
    print(Back.BLACK + f'{"":<80}')
    print(Fore.LIGHTGREEN_EX + Back.BLACK + f'{"":<4}{"[1] ПОИСКОВАЯ ФРАЗА":<40}{"[5] ПОИСКОВИК":<36}')
    print(Fore.LIGHTGREEN_EX + Back.BLACK + f'{"":<4}{"[2] URL ВЕБ-САЙТА":<40}{"[6] НАЧАТЬ ПРОСМОТР":<36}')
    print(Fore.LIGHTGREEN_EX + Back.BLACK + f'{"":<4}{"[3] МЕСТОПОЛОЖЕНИЕ (только для ЯНДЕКС)":<40}{"[7] ПРОСМОТР ДАННЫХ ЗАПРОСА":<36}')
    print(Fore.LIGHTGREEN_EX + Back.BLACK + f'{"":<4}{"[4] ТАЙМЕР":<40}{"[8] ПРОСМОТР ВЫХОДНЫХ ДАННЫХ":<36}')
    print(Back.BLACK + f'{"":<80}')
    print(Fore.LIGHTGREEN_EX + Back.BLACK + f'{"":<4}{"[Q] ВЫХОД":<76}')
    print(Back.BLACK + f'{"":<80}')


def search_engine_menu():
    print(f'{"":<4}{"[1] Yandex"}')
    print(f'{"":<4}{"[2] Google"}')


def get_string(msg, required=None, valid=None):
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


def get_integer(msg, required=None, valid=None):
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
        else:
            return int(line)


if __name__ == "__main__":
    search_engine_menu()
