#!/bin/bash

ACCT_ID="$(ibmcloud account show --output json | jq '.account_id')"
REGIONS="$(ibmcloud regions --output json  | jq '.[].Name'|sed 's/"//g')"
echo "account_name","name", "resource_type", "ip_address","region","type"

# floating ips - listing floating IPs in all resource groups and region $region"
function floatip_scanner () {
    
    for region in $REGIONS; do
        ibmcloud target -r $region > /dev/null 2>&1
        retVal=$?
        if [ $retVal -ne 0 ]
        then
            :
        else
            FLOAT_IPS="$(ibmcloud is ips --output json | jq -r '.[]|.name + "," + .target.resource_type + "," + .address')"
            if [ -z "$FLOAT_IPS" ]
            then
                echo "$ACCT_ID","NULL","NULL","NULL","$region","floating_ip"
            else
                for float in $FLOAT_IPS; do
                    echo "$ACCT_ID", "$float", "$region", "floating_ip"
                done
            fi
        fi
    done
}


# vsi private ips
function vsiips_scanner() {
    for region in $REGIONS; do
        ibmcloud target -r $region > /dev/null 2>&1
        VSI_IPS="$(ibmcloud is instances --output json | jq -r '.[]| .name + "," + .network_interfaces[].resource_type + "," + .network_interfaces[].primary_ipv4_address')"
        if [ -z "$VSI_IPS" ]
        then
            echo "$ACCT_ID","NULL","NULL","NULL","$region","vsi_private_ip"
        else
            for vsi_ip in $VSI_IPS; do
                echo "$ACCT_ID", "$vsi_ip", "$region", "vsi_private_ip"
            done
        fi
    done
}

# iks/roks worker nodes ips
function iksroks_scanner() {
    KS_CLUSTER="$(ibmcloud ks clusters --output json  | jq -r '.[].id')"
    for ks in $KS_CLUSTER ; do
        KS_IPS="$(ibmcloud ks workers -c $ks --output json | jq -r '.[]|.id + "," + .poolid + "," + .privateIP + "," + .publicIP')"
        for iksroks_ips in $KS_IPS ; do
            echo "$ACCT_ID", "$iksroks_ips", "iksroks_ip"
        done
    done
}

# run
floatip_scanner
vsiips_scanner
iksroks_scanner