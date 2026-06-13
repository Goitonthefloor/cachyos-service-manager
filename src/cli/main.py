"""CLI entry point."""

import click
from rich.console import Console
from rich.table import Table

try:
    from importlib.metadata import version
    __version__ = version("cachyos-service-manager")
except Exception:
    __version__ = "0.0.0"

from cachyos_service_manager.core.service_manager import ServiceManager, ServiceState

console = Console()


@click.group()
@click.version_option(version=__version__)
def cli():
    """CachyOS Service Manager CLI."""
    pass


@cli.command()
@click.argument('service', required=False)
@click.option('--type', 'service_type', type=click.Choice(['service', 'socket', 'timer', 'target', 'path', 'mount', 'device']),
              help='Filter by service type')
@click.option('--all', 'show_inactive', is_flag=True, default=False,
              help='Include inactive services')
def list(service, service_type, show_inactive):
    """List all services."""
    mgr = ServiceManager()
    services = mgr.list_all_services(
        service_type=service_type,
        show_inactive=show_inactive
    )

    if not services:
        console.print("[yellow]No services found.[/yellow]")
        return

    table = Table(title="Systemd Services")
    table.add_column("Name", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Enabled", justify="center")
    table.add_column("Description", style="gray")

    for svc in services:
        status_map = {
            ServiceState.ACTIVE: "[green]● active[/green]",
            ServiceState.INACTIVE: "[yellow]● inactive[/yellow]",
            ServiceState.FAILED: "[red]● failed[/red]",
            ServiceState.ACTIVATING: "[blue]● activating[/blue]",
            ServiceState.DEACTIVATING: "[magenta]● deactivating[/magenta]",
            ServiceState.UNKNOWN: "● unknown",
        }
        enabled_str = "[green]yes[/green]" if svc.enabled else "[red]no[/red]"
        table.add_row(
            svc.display_name,
            status_map.get(svc.state, "● unknown"),
            enabled_str,
            svc.description or "-"
        )

    console.print(table)


@cli.command()
@click.argument('service')
def status(service):
    """Show service status."""
    mgr = ServiceManager()
    svc = mgr.get_service_status(service)

    if svc is None:
        console.print(f"[red]Service '{service}' not found.[/red]")
        return

    console.print(f"\n[bold]Service:[/bold] {svc.display_name}")
    console.print(f"[bold]State:[/bold]     {svc.state.value}")
    console.print(f"[bold]Active:[/bold]    {svc.active_state}")
    console.print(f"[bold]Sub-state:[/bold] {svc.sub_state}")
    console.print(f"[bold]Enabled:[/bold] {'yes' if svc.enabled else 'no'}")
    console.print(f"[bold]PID:[/bold]       {svc.pid or 'N/A'}")
    if svc.memory:
        console.print(f"[bold]Memory:[/bold]  {svc.memory}")
    if svc.cpu:
        console.print(f"[bold]CPU:[/bold]     {svc.cpu}")
    if svc.description:
        console.print(f"[bold]Description:[/bold] {svc.description}")
    console.print()


@cli.command()
@click.argument('service')
def start(service):
    """Start a service."""
    mgr = ServiceManager()
    success, msg = mgr.start_service(service)
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


@cli.command()
@click.argument('service')
def stop(service):
    """Stop a service."""
    mgr = ServiceManager()
    success, msg = mgr.stop_service(service)
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


@cli.command()
@click.argument('service')
def restart(service):
    """Restart a service."""
    mgr = ServiceManager()
    success, msg = mgr.restart_service(service)
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


@cli.command()
@click.argument('service')
def enable(service):
    """Enable a service (autostart)."""
    mgr = ServiceManager()
    success, msg = mgr.enable_service(service)
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


@cli.command()
@click.argument('service')
def disable(service):
    """Disable a service (no autostart)."""
    mgr = ServiceManager()
    success, msg = mgr.disable_service(service)
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


@cli.command()
@click.argument('service')
@click.option('--lines', '-n', default=50, help='Number of log lines to show')
def logs(service, lines):
    """Show service logs."""
    mgr = ServiceManager()
    log_output = mgr.get_service_logs(service, lines=lines)
    if log_output:
        console.print(log_output)
    else:
        console.print("[yellow]No logs available.[/yellow]")


if __name__ == '__main__':
    cli()