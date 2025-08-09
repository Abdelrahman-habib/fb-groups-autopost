import sys
import os
import logging
import click
from .config import load_config
from .runner import run_posting


@click.group()
def main():
    """Facebook Groups Poster CLI"""


@main.command()
@click.option(
    "--config",
    "config_path",
    default="config.yaml",
    show_default=True,
    type=click.Path(dir_okay=False),
)
@click.option("-y", "assume_yes", is_flag=True, help="Skip confirmations and proceed")
@click.option("-v", "verbose", is_flag=True, help="Enable verbose (debug) logging")
def run(config_path: str, assume_yes: bool, verbose: bool):
    """Run poster with a YAML config"""
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    if not os.path.exists(config_path):
        click.echo(
            f"Config file not found at '{config_path}'. "
            "Create one by copying 'config.example.yaml' to 'config.yaml' and updating values, "
            "or pass --config <path> to use a different file.",
            err=True,
        )
        sys.exit(1)
    cfg = load_config(config_path)
    logger.debug("Loaded config from %s", config_path)
    success = run_posting(cfg, assume_yes=assume_yes)
    sys.exit(0 if success else 1)

