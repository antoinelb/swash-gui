import glob
import itertools
import shutil
from pathlib import Path

import typer

from src.dashboard import run_server
from src.utils.print import done_print, error_print, load_print

from .config import Config, read_config, write_config
from .simulation import run_simulation
from .utils.paths import root_dir

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
    cli.command("clean")(_clean)
    cli.command("cc", hidden=True)(_clean)
    return cli


def _create_or_update(
    files: list[str] = typer.Argument(
        ...,
        help="File(s) to create or update (a .yml extension will be added if missing)",
    ),
) -> None:
    """
    (c) Creates or updates experiment config files with defaults.
    """
    files = [f"{file}.yml" if not file.endswith(".yml") else file for file in files]
    for file in _expand_paths(files):
        path = Path(file)
        try:
            config = read_config(path)
            write_config(config, path)
            done_print(f"Updated config {file}.")
        except FileNotFoundError:
            config = Config(name=path.stem)
            write_config(config, path)
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
        write_config(config, path)
        run_simulation(config)


def _run_dashboard() -> None:
    """
    (d) Runs the dashboard
    """
    run_server()


def _clean(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what would be deleted without actually deleting",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """
    (cc) Clean up simulation directories that don't have corresponding configs.

    This command removes simulation directories in the simulations/ folder that
    don't correspond to any configuration file in the config/ directory.
    """
    config_dir = root_dir / "config"
    simulations_dir = root_dir / "simulations"

    if not simulations_dir.exists():
        done_print("No simulations directory found, nothing to clean.")
        return

    # Get all config names and their hashes
    config_hashes = {}
    if config_dir.exists():
        for config_file in config_dir.glob("*.yml"):
            try:
                config = read_config(config_file)
                config_hashes[config.name] = config.hash
            except Exception as e:
                error_print(f"Error reading config {config_file}: {e}")

    # Find orphaned simulation directories
    orphaned_dirs = []
    for sim_dir in simulations_dir.iterdir():
        if not sim_dir.is_dir():
            continue

        # Parse directory name (format: <name>_<hash>)
        parts = sim_dir.name.rsplit("_", 1)
        if len(parts) != 2:
            orphaned_dirs.append(sim_dir)
            continue

        name, dir_hash = parts

        # Check if this corresponds to a current config
        if name not in config_hashes or config_hashes[name] != dir_hash:
            orphaned_dirs.append(sim_dir)

    if not orphaned_dirs:
        done_print("No orphaned simulation directories found.")
        return

    # Show what will be deleted
    load_print(f"Found {len(orphaned_dirs)} orphaned simulation directories:")
    for dir_path in orphaned_dirs:
        print(f"  - {dir_path.relative_to(root_dir)}")

    if dry_run:
        done_print("Dry run complete. No directories were deleted.")
        return

    # Confirm deletion
    if not force:
        confirm = typer.confirm("Delete these directories?")
        if not confirm:
            print("Cancelled.")
            return

    # Delete directories
    deleted_count = 0
    for dir_path in orphaned_dirs:
        try:
            shutil.rmtree(dir_path)
            deleted_count += 1
        except Exception as e:
            error_print(f"Error deleting {dir_path}: {e}")

    done_print(f"Deleted {deleted_count} orphaned simulation directories.")




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
