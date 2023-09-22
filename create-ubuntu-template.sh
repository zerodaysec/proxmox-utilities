#!/bin/bash
set -e

TEMPLATE_NAME="ubuntu-${RELEASE}-template"
DATA_STORE="local-lvm"
VM_BRIDGE="vmbr0"


# Check if exactly two arguments are passed
if [ "$#" -ne 2 ]; then
    echo "You must enter exactly 2 arguments: release, TEMPLATE_ID"
    exit 1
fi

# Assign arguments to variables
RELEASE="$1"
TEMPLATE_ID="$2"

# Array of valid src_ids
UBUNTU_RELEASES=("jammy" "focal" "bionic")

# Check if src_id is valid
VALID=false
for id in "${UBUNTU_RELEASES[@]}"; do
    if [ "$RELEASE" == "$id" ]; then
        VALID=true
        break
    fi
done

if [ "$VALID" = true ]; then
    echo "Creating template for release: $RELEASE"
else
    echo "Error: Invalid release. Must be one of: ${UBUNTU_RELEASES[@]}"
    exit 1
fi

# Check if dest_value is greater than 9000
if [ "$TEMPLATE_ID" -gt 9000 ]; then
    echo "TEMPLATE_ID: $TEMPLATE_ID is greater than 9000"
else
    echo "Error: Destination Value must be greater than 9000."
    exit 1
fi

# Get the ubuntu relase image
wget "https://cloud-images.ubuntu.com/${RELEASE}/current/${RELEASE}-server-cloudimg-amd64.img"

# Create a VM
qm create "${TEMPLATE_ID} "--name "${TEMPLATE_NAME}" --memory 2048 --net0 virtio,bridge=${VM_BRIDGE}

qm importdisk "$TEMPLATE_ID" "${RELEASE}-server-cloudimg-amd64.img" $DATA_STORE -format qcow2

qm set"$TEMPLATE_ID"--scsihw virtio-scsi-pci --scsi0 $DATA_STORE:"vm-$TEMPLATE_ID-disk-0"

qm set"$TEMPLATE_ID"--ide2 local:cloudinit --boot c --bootdisk scsi0 --serial0 socket --vga serial0

qm resize"$TEMPLATE_ID"scsi0 +30G

qm set"$TEMPLATE_ID"--ipconfig0 ip=dhcp

qm set"$TEMPLATE_ID"--sshkey ~/id_rsa.pub

qm cloudinit dump "$TEMPLATE_ID" user

qm template "$TEMPLATE_ID"
