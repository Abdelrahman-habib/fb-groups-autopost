import sys
import os
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
def run(config_path: str):
    """Run poster with a YAML config"""
    if not os.path.exists(config_path):
        click.echo(
            f"Config file not found at '{config_path}'. "
            "Create one by copying 'config.example.yaml' to 'config.yaml' and updating values, "
            "or pass --config <path> to use a different file.",
            err=True,
        )
        sys.exit(1)
    cfg = load_config(config_path)
    success = run_posting(cfg)
    sys.exit(0 if success else 1)

