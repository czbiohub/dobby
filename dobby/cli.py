import click

from dobby.cherrypick import cherrypick

settings = dict(help_option_names=['-h', '--help'])


@click.group(options_metavar='', subcommand_metavar='<command>',
             context_settings=settings)
def cli():
    """
    Hi! Dobby is the heroic house-elf that automates SampleSheet generation 
    from Google Sheets. And, of course, Dobby is free.
    """
    pass


cli.add_command(cherrypick)


if __name__ == "__main__":
    cli()