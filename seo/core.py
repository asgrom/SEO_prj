import click

from seo import seo_urwid, seo_console, seo_qt


@click.command()
@click.option('--urwid', '-u', help='Запуск с urwid-меню (по-умолчанию)', is_flag=True)
@click.option('--console', '-c', help='Запуск с консольным меню', is_flag=True)
@click.option('--qt', '-q', help='Qt версия', is_flag=True, default=True)
@click.option('--proxy', '-p', help='Прокси сервер')
@click.help_option('-h', '--help', help='Показать эту справку')
def cli(urwid, console, qt, proxy):
    """Запускает seo-sprint

    По-умолчанию запускается с urwid-меню"""
    if qt:
        seo_qt.main(proxy)
    # if urwid and not console:
    #     seo_urwid.main()
    # elif console:
    #     seo_console.main()


if __name__ == '__main__':
    cli()
