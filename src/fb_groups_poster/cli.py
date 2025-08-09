import sys
import click
from .config import load_config
from .runner import run_posting


@click.group()
def main():
    """Facebook Groups Poster CLI"""


@main.command()
@click.option("--config", "config_path", required=True, type=click.Path(exists=True, dir_okay=False))
def run(config_path: str):
    """Run poster with a YAML config"""
    cfg = load_config(config_path)
    success = run_posting(cfg)
    sys.exit(0 if success else 1)

