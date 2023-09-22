#!/bin/bash

################################################################################
# Name: create-vm.sh $SRC_ID $DEST_NAME
# Author: jon@zer0day.net
# Purpose: This will clone a proxmov vm template and create a new vm based on
#          the name provided.
################################################################################

# Check if exactly two arguments are passed
if [ "$#" -ne 2 ]; then
    echo "You must enter exactly 2 arguments: src_id and dest_name."
    exit 1
fi

# Assign arguments to variables
TEMPLATE_ID="$1"
DEST_NAME="$2"
DATA_STORE="local-lvm"

# Print the values (or you can process them further as needed)
echo "Source ID: $TEMPLATE_ID"
echo "Destination Name: $DEST_NAME"
# exit

# Continue with the rest of our logic
echo qm clone ${TEMPLATE_ID} 190 --name ${DEST_NAME}
echo qm set ${TEMPLATE_ID} --ide2 $DATA_STORE:cloudinit --boot c --bootdisk scsi0 --serial0 socket --vga serial0
