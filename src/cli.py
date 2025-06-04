import glob
import itertools
from pathlib import Path

import typer

from src.utils.print import done_print

from .config import Config, read_config, save_config
from .simulation import run_simulation

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
    cli.command("create")(_create_or_update)
    cli.command("c", hidden=True)(_create_or_update)
    cli.command("run")(_run)
    cli.command("r", hidden=True)(_run)
    cli.command("dashboard")(_run_dashboard)
    cli.command("d", hidden=True)(_run_dashboard)
    return cli


def _create_or_update(
    files: list[str] = typer.Argument(
        ...,
        help="File(s) to create or update (a .yml extension will be added "
        "if missing)",
    )
) -> None:
    """
    (c) Creates or updates experiment config files with defaults.
    """
    files = [
        f"{file}.yml" if not file.endswith(".yml") else file for file in files
    ]
    for file in _expand_paths(files):
        path = Path(file)
        try:
            config = read_config(path)
            save_config(config, path)
            done_print(f"Updated config {file}.")
        except FileNotFoundError:
            config = Config(name=path.stem)
            save_config(config, path)
            done_print(f"Created config {file}.")


def _run(
    configs: list[str] = typer.Argument(
        ...,
        help="Files or directories containing the experiment configuration",
    ),
) -> None:
    """
    (r) Runs the experiment.
    """
    for config_ in _expand_paths(configs):
        path = Path(config_)
        config = read_config(path)
        save_config(config, path)
        run_simulation(config)


def _run_dashboard() -> None:
    """
    (d) Runs the dashboard
    """
    from src.dashboard import create_app

    app = create_app()
    done_print("Starting dashboard at http://127.0.0.1:8000")
    app.run(debug=False, host="127.0.0.1", port=8000)


def _expand_paths(paths: list[str]) -> list[Path]:
    """
    Expand a list of path patterns into a list of actual file paths.

    This function handles glob patterns and returns a sorted list of unique paths.
    Non-directory paths are included directly, and directories are searched for *.yml files.

    Parameters
    ----------
    paths : list[str]
        List of path patterns to expand

    Returns
    -------
    list[Path]
        Sorted list of unique paths matching the patterns
    """
    paths_ = list(
        set(map(Path, itertools.chain(*(glob.glob(path) for path in paths))))
        | {Path(path) for path in paths if "*" not in path}
    )
    return sorted(
        [
            *[p for p in paths_ if not p.is_dir()],
            *itertools.chain(*(p.glob("**/*.yml") for p in paths_)),
        ]
    )
