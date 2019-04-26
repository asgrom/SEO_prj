from colorama import init, Fore, Style, Back
from seo.core import *

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

if __name__ == "__main__":
        while True:
            get
        main_menu()
        
