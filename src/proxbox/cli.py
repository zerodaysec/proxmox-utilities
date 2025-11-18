"""
Command-line interface for ProxBox.

This module provides CLI commands for template and VM management.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from proxbox import __version__
from proxbox.config import ProxmoxConfig
from proxbox.exceptions import ProxmoxUtilityError
from proxbox.template import TemplateCreator, UbuntuRelease
from proxbox.vm import VMCreator

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="proxbox")
@click.pass_context
def main(ctx: click.Context) -> None:
    """
    ProxBox - Your Proxmox toolbox for secure VM automation.

    Manage Proxmox VE templates and virtual machines with ease.

    \b
    Examples:
        # Create an Ubuntu 22.04 template
        proxbox create-template jammy 9001

        # Clone a VM from a template
        proxbox create-vm 9001 190 my-ubuntu-vm

        # Create and start a VM
        proxbox create-vm 9001 191 web-server --start
    """
    ctx.ensure_object(dict)


@main.command(name="create-template")
@click.argument("release", type=click.Choice([r.value for r in UbuntuRelease]))
@click.argument("template_id", type=int)
@click.option(
    "--name",
    "-n",
    "template_name",
    help="Template name (default: ubuntu-{release}-template)",
)
@click.option(
    "--memory",
    "-m",
    type=int,
    help="Memory in MB (default: 2048)",
)
@click.option(
    "--disk-increase",
    "-d",
    type=int,
    help="Disk size increase in GB (default: 30)",
)
@click.option(
    "--ssh-key",
    "-k",
    type=click.Path(exists=True, path_type=Path),
    help="Path to SSH public key",
)
@click.option(
    "--data-store",
    "-s",
    help="Proxmox data store (default: local-lvm)",
)
@click.option(
    "--keep-image",
    is_flag=True,
    help="Keep downloaded image file after template creation",
)
def create_template(
    release: str,
    template_id: int,
    template_name: Optional[str],
    memory: Optional[int],
    disk_increase: Optional[int],
    ssh_key: Optional[Path],
    data_store: Optional[str],
    keep_image: bool,
) -> None:
    """
    Create an Ubuntu cloud-init template.

    \b
    RELEASE: Ubuntu release (jammy, focal, noble)
    TEMPLATE_ID: VM ID for the template (recommended: > 9000)

    \b
    Examples:
        # Create Ubuntu 22.04 LTS template
        proxmox create-template jammy 9001

        # Create template with custom settings
        proxmox create-template noble 9002 \\
            --name my-ubuntu-template \\
            --memory 4096 \\
            --disk-increase 50 \\
            --ssh-key ~/.ssh/id_ed25519.pub

    \b
    Environment Variables:
        PROXMOX_SSH_KEY_PATH    Path to SSH public key
        PROXMOX_DATA_STORE      Proxmox data store name
        PROXMOX_VM_BRIDGE       Network bridge name
    """
    try:
        # Build configuration
        config_kwargs = {}
        if ssh_key:
            config_kwargs["ssh_key_path"] = ssh_key
        if data_store:
            config_kwargs["data_store"] = data_store

        config = ProxmoxConfig(**config_kwargs)
        creator = TemplateCreator(config)

        # Create template
        creator.create_template(
            release=UbuntuRelease(release),
            template_id=template_id,
            template_name=template_name,
            memory_mb=memory,
            disk_increase_gb=disk_increase,
            keep_image=keep_image,
        )

    except ProxmoxUtilityError as e:
        console.print(f"[red]Error:[/red] {e}", err=True)
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}", err=True)
        sys.exit(2)


@main.command(name="create-vm")
@click.argument("template_id", type=int)
@click.argument("vm_id", type=int)
@click.argument("vm_name")
@click.option(
    "--start",
    is_flag=True,
    help="Start the VM after creation",
)
@click.option(
    "--no-network",
    is_flag=True,
    help="Skip network configuration",
)
@click.option(
    "--data-store",
    "-s",
    help="Proxmox data store (default: local-lvm)",
)
def create_vm(
    template_id: int,
    vm_id: int,
    vm_name: str,
    start: bool,
    no_network: bool,
    data_store: Optional[str],
) -> None:
    """
    Create a VM by cloning a template.

    \b
    TEMPLATE_ID: Source template ID to clone from
    VM_ID: New VM ID (must be unique)
    VM_NAME: Name for the new VM (alphanumeric, hyphens, underscores)

    \b
    Examples:
        # Create a VM from template
        proxmox create-vm 9001 190 my-ubuntu-vm

        # Create and start a VM
        proxmox create-vm 9001 191 web-server --start

        # Create VM without network config
        proxmox create-vm 9001 192 db-server --no-network

    \b
    Environment Variables:
        PROXMOX_DATA_STORE      Proxmox data store name
        PROXMOX_VM_BRIDGE       Network bridge name
    """
    try:
        # Build configuration
        config_kwargs = {}
        if data_store:
            config_kwargs["data_store"] = data_store

        config = ProxmoxConfig(**config_kwargs)
        creator = VMCreator(config)

        # Create VM
        creator.create_vm(
            template_id=template_id,
            vm_id=vm_id,
            vm_name=vm_name,
            start_vm=start,
            configure_network=not no_network,
        )

    except ProxmoxUtilityError as e:
        console.print(f"[red]Error:[/red] {e}", err=True)
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}", err=True)
        sys.exit(2)


@main.command(name="start")
@click.argument("vm_id", type=int)
def start_vm(vm_id: int) -> None:
    """
    Start a VM.

    \b
    VM_ID: VM ID to start

    \b
    Example:
        proxmox start 190
    """
    try:
        creator = VMCreator()
        creator.start_vm(vm_id)
    except ProxmoxUtilityError as e:
        console.print(f"[red]Error:[/red] {e}", err=True)
        sys.exit(1)


@main.command(name="stop")
@click.argument("vm_id", type=int)
@click.option(
    "--force",
    is_flag=True,
    help="Force stop (hard shutdown)",
)
def stop_vm(vm_id: int, force: bool) -> None:
    """
    Stop a VM.

    \b
    VM_ID: VM ID to stop

    \b
    Examples:
        # Graceful shutdown
        proxmox stop 190

        # Force stop
        proxmox stop 190 --force
    """
    try:
        creator = VMCreator()
        creator.stop_vm(vm_id, force=force)
    except ProxmoxUtilityError as e:
        console.print(f"[red]Error:[/red] {e}", err=True)
        sys.exit(1)


@main.command(name="status")
@click.argument("vm_id", type=int)
def vm_status(vm_id: int) -> None:
    """
    Get VM status.

    \b
    VM_ID: VM ID to check

    \b
    Example:
        proxmox status 190
    """
    try:
        creator = VMCreator()
        status = creator.get_vm_status(vm_id)

        console.print(f"\n[bold cyan]VM {vm_id} Status:[/bold cyan]")
        for key, value in status.items():
            console.print(f"  {key}: {value}")
        console.print()

    except ProxmoxUtilityError as e:
        console.print(f"[red]Error:[/red] {e}", err=True)
        sys.exit(1)


@main.command(name="delete")
@click.argument("vm_id", type=int)
@click.option(
    "--no-purge",
    is_flag=True,
    help="Don't remove from backup storage",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompt",
)
def delete_vm(vm_id: int, no_purge: bool, yes: bool) -> None:
    """
    Delete a VM.

    \b
    VM_ID: VM ID to delete

    \b
    Warning: This operation is irreversible!

    \b
    Examples:
        # Delete with confirmation
        proxmox delete 190

        # Delete without confirmation
        proxmox delete 190 --yes
    """
    try:
        if not yes:
            console.print(
                f"[yellow]Warning:[/yellow] You are about to delete VM {vm_id}. "
                "This cannot be undone!"
            )
            if not click.confirm("Are you sure?"):
                console.print("Cancelled.")
                return

        creator = VMCreator()
        creator.delete_vm(vm_id, purge=not no_purge)

    except ProxmoxUtilityError as e:
        console.print(f"[red]Error:[/red] {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
