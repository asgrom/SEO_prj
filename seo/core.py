import click

from seo import seo_urwid, seo_console


@click.command()
@click.option('--urwid', '-u', help='Запуск с urwid-меню (по-умолчанию)', is_flag=True, default=True)
@click.option('--console', '-c', help='Запуск с консольным меню', is_flag=True)
def cli(urwid=None, console=None):
    """Запускает seo-sprint

    По-умолчанию запускается с urwid-меню"""

    if urwid and not console:
        seo_urwid.main()
    elif console:
        seo_console.main()


if __name__ == '__main__':
    cli()
