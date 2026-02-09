"""CLI entry point."""

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """CachyOS Service Manager CLI."""
    pass


@cli.command()
@click.argument('service')
def status(service):
    """Show service status."""
    console.print(f"[yellow]Status for {service} - Not yet implemented[/yellow]")


@cli.command()
@click.argument('service')
def start(service):
    """Start a service."""
    console.print(f"[yellow]Starting {service} - Not yet implemented[/yellow]")


@cli.command()
@click.argument('service')
def stop(service):
    """Stop a service."""
    console.print(f"[yellow]Stopping {service} - Not yet implemented[/yellow]")


@cli.command()
def list():
    """List all services."""
    console.print("[yellow]Listing services - Not yet implemented[/yellow]")


if __name__ == '__main__':
    cli()