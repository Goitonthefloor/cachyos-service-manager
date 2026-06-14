"""CLI entry point."""

import click
from rich.console import Console
from rich.table import Table
from pathlib import Path

try:
    from importlib.metadata import version
    __version__ = version("cachyos-service-manager")
except Exception:
    __version__ = "0.0.0"

from core.service_manager import ServiceManager, ServiceState, ServiceType
from core.service_group import ServiceGroupManager

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


@cli.command()
@click.option('--all', 'show_inactive', is_flag=True, default=True,
              help='Include inactive timers')
def timers(show_inactive):
    """List all systemd timers."""
    mgr = ServiceManager()
    timer_list = mgr.list_timers(show_inactive=show_inactive)

    if not timer_list:
        console.print("[yellow]No timers found.[/yellow]")
        return

    table = Table(title="Systemd Timers")
    table.add_column("Name", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Enabled", justify="center")
    table.add_column("Description", style="gray")

    for svc in timer_list:
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
@click.argument('timer')
def timer_status(timer):
    """Show timer status."""
    mgr = ServiceManager()
    svc = mgr.get_timer_status(timer)

    if svc is None:
        console.print(f"[red]Timer '{timer}' not found.[/red]")
        return

    console.print(f"\n[bold]Timer:[/bold] {svc.display_name}")
    console.print(f"[bold]State:[/bold]     {svc.state.value}")
    console.print(f"[bold]Active:[/bold]    {svc.active_state}")
    console.print(f"[bold]Sub-state:[/bold] {svc.sub_state}")
    console.print(f"[bold]Enabled:[/bold] {'yes' if svc.enabled else 'no'}")
    if svc.description:
        console.print(f"[bold]Description:[/bold] {svc.description}")
    console.print()


@cli.command()
def timer_list():
    """Show next timer activations."""
    mgr = ServiceManager()
    activations = mgr.get_next_timer_activations()

    if not activations:
        console.print("[yellow]No timer activations found.[/yellow]")
        return

    table = Table(title="Next Timer Activations")
    table.add_column("Next", style="cyan")
    table.add_column("Left", justify="center")
    table.add_column("Last", justify="center")
    table.add_column("Passed", justify="center")
    table.add_column("Unit", style="green")
    table.add_column("Activates", style="yellow")

    for act in activations:
        table.add_row(
            act['next'],
            act['left'],
            act['last'],
            act['passed'],
            act['unit'],
            act['activates']
        )

    console.print(table)


@cli.command()
@click.option('--all', 'show_inactive', is_flag=True, default=True,
              help='Include inactive sockets')
def sockets(show_inactive):
    """List all systemd sockets."""
    mgr = ServiceManager()
    socket_list = mgr.list_sockets(show_inactive=show_inactive)

    if not socket_list:
        console.print("[yellow]No sockets found.[/yellow]")
        return

    table = Table(title="Systemd Sockets")
    table.add_column("Name", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Enabled", justify="center")
    table.add_column("Description", style="gray")

    for svc in socket_list:
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
@click.argument('socket')
def socket_status(socket):
    """Show socket status."""
    mgr = ServiceManager()
    svc = mgr.get_socket_status(socket)

    if svc is None:
        console.print(f"[red]Socket '{socket}' not found.[/red]")
        return

    console.print(f"\n[bold]Socket:[/bold] {svc.display_name}")
    console.print(f"[bold]State:[/bold]     {svc.state.value}")
    console.print(f"[bold]Active:[/bold]    {svc.active_state}")
    console.print(f"[bold]Sub-state:[/bold] {svc.sub_state}")
    console.print(f"[bold]Enabled:[/bold] {'yes' if svc.enabled else 'no'}")
    if svc.description:
        console.print(f"[bold]Description:[/bold] {svc.description}")
    console.print()


@cli.group()
def group():
    """Manage service groups."""
    pass


@group.command('create')
@click.argument('name')
@click.argument('services', nargs=-1)
@click.option('--description', '-d', default='', help='Group description')
@click.option('--color', '-c', default='#3daee9', help='Group color (hex)')
@click.option('--icon', '-i', default='⚙️', help='Group icon (emoji)')
def group_create(name, services, description, color, icon):
    """Create a new service group."""
    mgr = ServiceGroupManager()
    try:
        group = mgr.create_group(
            name=name,
            description=description,
            services=list(services),
            color=color,
            icon=icon
        )
        console.print(f"[green]✓ Created group '{name}' with {len(services)} services[/green]")
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")


@group.command('delete')
@click.argument('name')
def group_delete(name):
    """Delete a service group."""
    mgr = ServiceGroupManager()
    if name in [g.name for g in mgr.list_groups()]:
        mgr.delete_group(name)
        console.print(f"[green]✓ Deleted group '{name}'[/green]")
    else:
        console.print(f"[red]✗ Group '{name}' not found[/red]")


@group.command('list')
def group_list():
    """List all service groups."""
    mgr = ServiceGroupManager()
    groups = mgr.list_groups()
    if not groups:
        console.print("[yellow]No groups found.[/yellow]")
        return
    
    table = Table(title="Service Groups")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="gray")
    table.add_column("Services", justify="center")
    table.add_column("Color")
    table.add_column("Icon")
    
    for g in groups:
        table.add_row(g.name, g.description, str(len(g.services)), g.color, g.icon)
    
    console.print(table)


@group.command('show')
@click.argument('name')
def group_show(name):
    """Show details of a service group."""
    mgr = ServiceGroupManager()
    group = mgr.get_group(name)
    if not group:
        console.print(f"[red]Group '{name}' not found[/red]")
        return
    
    console.print(f"\n[bold]Group:[/bold] {group.name}")
    console.print(f"[bold]Description:[/bold] {group.description or '—'}")
    console.print(f"[bold]Color:[/bold] {group.color}")
    console.print(f"[bold]Icon:[/bold] {group.icon}")
    console.print(f"[bold]Auto-start order:[/bold] {group.auto_start_order}")
    console.print(f"[bold]Services:[/bold]")
    for svc in group.services:
        console.print(f"  • {svc}")


@group.command('templates')
def group_templates():
    """List predefined group templates."""
    mgr = ServiceGroupManager()
    templates = mgr.get_predefined_groups()
    
    table = Table(title="Predefined Group Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="gray")
    table.add_column("Services", justify="center")
    table.add_column("Color")
    table.add_column("Icon")
    
    for t in templates:
        table.add_row(t['name'], t['description'], str(len(t['services'])), t['color'], t['icon'])
    
    console.print(table)


@group.command('create-from-template')
@click.argument('template_name')
def group_create_from_template(template_name):
    """Create a group from a predefined template."""
    mgr = ServiceGroupManager()
    group = mgr.create_group_from_template(template_name)
    if group:
        console.print(f"[green]✓ Created group '{group.name}' from template with {len(group.services)} services[/green]")
    else:
        console.print(f"[red]✗ Template '{template_name}' not found[/red]")


@group.command('start')
@click.argument('name')
def group_start(name):
    """Start all services in a group."""
    mgr = ServiceGroupManager()
    group = mgr.get_group(name)
    if not group:
        console.print(f"[red]Group '{name}' not found[/red]")
        return
    
    svc_mgr = ServiceManager()
    for svc in group.services:
        success, msg = svc_mgr.start_service(svc)
        if success:
            console.print(f"[green]✓ Started {svc}[/green]")
        else:
            console.print(f"[red]✗ Failed to start {svc}: {msg}[/red]")


@group.command('stop')
@click.argument('name')
def group_stop(name):
    """Stop all services in a group."""
    mgr = ServiceGroupManager()
    group = mgr.get_group(name)
    if not group:
        console.print(f"[red]Group '{name}' not found[/red]")
        return
    
    svc_mgr = ServiceManager()
    for svc in group.services:
        success, msg = svc_mgr.stop_service(svc)
        if success:
            console.print(f"[green]✓ Stopped {svc}[/green]")
        else:
            console.print(f"[red]✗ Failed to stop {svc}: {msg}[/red]")


@group.command('restart')
@click.argument('name')
def group_restart(name):
    """Restart all services in a group."""
    mgr = ServiceGroupManager()
    group = mgr.get_group(name)
    if not group:
        console.print(f"[red]Group '{name}' not found[/red]")
        return
    
    svc_mgr = ServiceManager()
    for svc in group.services:
        success, msg = svc_mgr.restart_service(svc)
        if success:
            console.print(f"[green]✓ Restarted {svc}[/green]")
        else:
            console.print(f"[red]✗ Failed to restart {svc}: {msg}[/red]")


@group.command('enable')
@click.argument('name')
def group_enable(name):
    """Enable all services in a group (autostart)."""
    mgr = ServiceGroupManager()
    group = mgr.get_group(name)
    if not group:
        console.print(f"[red]Group '{name}' not found[/red]")
        return
    
    svc_mgr = ServiceManager()
    for svc in group.services:
        success, msg = svc_mgr.enable_service(svc)
        if success:
            console.print(f"[green]✓ Enabled {svc}[/green]")
        else:
            console.print(f"[red]✗ Failed to enable {svc}: {msg}[/red]")


@group.command('disable')
@click.argument('name')
def group_disable(name):
    """Disable all services in a group (no autostart)."""
    mgr = ServiceGroupManager()
    group = mgr.get_group(name)
    if not group:
        console.print(f"[red]Group '{name}' not found[/red]")
        return
    
    svc_mgr = ServiceManager()
    for svc in group.services:
        success, msg = svc_mgr.disable_service(svc)
        if success:
            console.print(f"[green]✓ Disabled {svc}[/green]")
        else:
            console.print(f"[red]✗ Failed to disable {svc}: {msg}[/red]")


@group.command('export')
@click.argument('name')
@click.argument('output_file', type=click.Path())
def group_export(name, output_file):
    """Export a group to JSON file."""
    import json
    mgr = ServiceGroupManager()
    group = mgr.get_group(name)
    if not group:
        console.print(f"[red]Group '{name}' not found[/red]")
        return
    
    data = group.to_dict()
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    console.print(f"[green]✓ Exported group '{name}' to {output_file}[/green]")


@group.command('import')
@click.argument('input_file', type=click.Path(exists=True))
def group_import(input_file):
    """Import a group from JSON file."""
    import json
    mgr = ServiceGroupManager()
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    group = ServiceGroup.from_dict(data)
    try:
        mgr.create_group(
            name=group.name,
            description=group.description,
            services=group.services,
            color=group.color,
            icon=group.icon
        )
        console.print(f"[green]✓ Imported group '{group.name}'[/green]")
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")


@cli.command()
@click.argument('services', nargs=-1, required=True)
@click.argument('output_file', type=click.Path())
def backup(services, output_file):
    """Backup service unit files and enabled state to JSON."""
    mgr = ServiceManager()
    success, msg = mgr.backup_services(list(services), output_file)
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def restore(input_file):
    """Restore service unit files and enabled state from JSON backup."""
    mgr = ServiceManager()
    success, msg = mgr.restore_services(input_file)
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


@cli.command()
@click.argument('service')
def unit_file(service):
    """Show unit file content for a service."""
    mgr = ServiceManager()
    content = mgr.get_unit_file(service)
    if content:
        console.print(content)
    else:
        console.print(f"[red]Service '{service}' not found or no unit file.[/red]")


@cli.command()
@click.option('--blame', is_flag=True, help='Show time taken by each unit')
@click.option('--critical-chain', is_flag=True, help='Show critical chain')
def analyze(blame, critical_chain):
    """Run systemd-analyze for boot performance analysis."""
    import subprocess
    try:
        if blame:
            result = subprocess.run(['systemd-analyze', 'blame'], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                console.print(result.stdout)
            else:
                console.print(f"[red]Error: {result.stderr}[/red]")
        elif critical_chain:
            result = subprocess.run(['systemd-analyze', 'critical-chain'], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                console.print(result.stdout)
            else:
                console.print(f"[red]Error: {result.stderr}[/red]")
        else:
            # Default: show overall boot time
            result = subprocess.run(['systemd-analyze'], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                console.print(result.stdout)
            else:
                console.print(f"[red]Error: {result.stderr}[/red]")
    except FileNotFoundError:
        console.print("[red]systemd-analyze not found. Is systemd installed?[/red]")
    except subprocess.TimeoutExpired:
        console.print("[red]Timeout running systemd-analyze[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument('service')
def dependencies(service):
    """Show service dependencies."""
    import subprocess
    try:
        if not service.endswith('.service'):
            service += '.service'
        
        result = subprocess.run(['systemctl', 'list-dependencies', service], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            console.print(result.stdout)
        else:
            console.print(f"[red]Error: {result.stderr}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument('service')
def dependents(service):
    """Show reverse dependencies (what depends on this service)."""
    import subprocess
    try:
        if not service.endswith('.service'):
            service += '.service'
        
        result = subprocess.run(['systemctl', 'list-dependencies', '--reverse', service], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            console.print(result.stdout)
        else:
            console.print(f"[red]Error: {result.stderr}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == '__main__':
    cli()
