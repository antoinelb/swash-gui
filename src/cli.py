import typer

############
# external #
############


def run_cli() -> None:
    """
    Main entry point for the CLI application.

    This function initializes the CLI and runs it.
    """
    cli = _init_cli()
    cli()


############
# internal #
############


def _init_cli() -> typer.Typer:
    """
    Initialize the CLI application with commands.

    Returns
    -------
    typer.Typer
        Configured Typer CLI object with registered commands
    """
    cli = typer.Typer(
        context_settings={"help_option_names": ["-h", "--help"]},
        pretty_exceptions_enable=False,
        pretty_exceptions_show_locals=False,
    )
    cli.command("run")(_run_dashboard)
    cli.command("r", hidden=True)(_run_dashboard)
    return cli


def _run_dashboard() -> None:
    """
    (r) Runs the dashboard
    """
    pass
