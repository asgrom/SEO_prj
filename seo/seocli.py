import click

from seo import core, seo_console, seo_qt


@click.command()
@click.option('--urwid', '-u', help='Запуск с urwid-меню (по-умолчанию)', is_flag=True)
@click.option('--console', '-c', help='Запуск с консольным меню', is_flag=True)
@click.option('--qt', '-q', help='Qt версия', is_flag=True, default=True)
@click.option('--no-user-dir', '-d', 'user_dir',
              help='не использовать --user-dir', is_flag=True, default=True)
@click.option('--incognito', '-i', help='использовать режим инкогнито',
              is_flag=True, default=False)
@click.option('--proxy', '-p', help='Прокси сервер')
@click.help_option('-h', '--help', help='Показать эту справку')
def cli(urwid, console, qt, user_dir, proxy, incognito):
    """
        Запускает seo-sprint

        По-умолчанию запускается с urwid-меню
    """
    # print(f'qt = {qt}, console = {console}, urwid = {urwid}')

    if qt:
        seo_qt.main(proxy=proxy, user_dir=user_dir, incognito=incognito)

    # if urwid and not console:
    #     seo_urwid.main()
    # elif console:
    #     seo_console.main()


if __name__ == '__main__':
    cli()
