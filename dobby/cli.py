import click

from dobby.echo_pick_lists import make_echo_pick_lists

settings = dict(help_option_names=['-h', '--help'])


@click.group(options_metavar='', subcommand_metavar='<command>',
             context_settings=settings)
def cli():
    """
    Hi! Dobby is a free and open source package for converting and managing 
    cDNA concentration files, ECHO pick lists, and sample sheets
    """
    pass


cli.add_command(make_echo_pick_lists)


if __name__ == "__main__":
    cli()