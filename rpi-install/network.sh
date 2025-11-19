#!/bin/bash

AP_CONFIG=./config/dhcpcd.conf.ap
WIFI_CONFIG=./config/dhcpcd.conf.wifi
WPA_CONFIG=/etc/wpa_supplicant/wpa_supplicant.conf

function usage() {
    echo "Usage:"
    echo "-a: Activate the Access Point"
    echo "-c: Configure new Wi-Fi Network"
    echo "    -s: SSID of the network"
    echo "    -p: Passphrase"
    echo "-w: Activate the Wi-Fi Network"
}

function activate_ap() {
    echo "Activating AP"
    sudo cp "$AP_CONFIG" /etc/dhcpcd.conf
    sudo systemctl enable hostapd.service
    echo "Rebooting system..."
    echo "After boot you can connect to the SSID=smartmeter"
    echo "The device can be accessed on the IP=192.168.10.1"
    echo ""
    sudo reboot
}


function deactivate_ap() {
    echo "Deactivating AP"
    sudo cp "$WIFI_CONFIG" /etc/dhcpcd.conf
    sudo systemctl disable hostapd.service
    echo "Rebooting system..."
    echo "After boot your device will be connected to the Wi-Fi router"
    echo "Please check the new IP or use the HOSTNAME=${HOSTNAME}"
    echo ""
    sudo reboot
}



ON=
OFF=
CONFIG=
SSID=
PW=
LIST=

optstring=":awcs:p:hl"

while getopts "$optstring" arg
do
    case ${arg} in
        a)
            ON='true'
            ;;
        w) 
            OFF='true'
            ;;
        c)
            CONFIG='true' 
            ;;
        s)
            SSID="$OPTARG"
            ;;
        p)
            PW="$OPTARG"
            ;;
        l) 
            LIST='true'
            ;; 
        h) 
            usage
            ;;
        :)
            echo "$0: Must supply an argument to -$OPTARG." >&2
            usage
            exit 1
            ;;
        ?)
            echo "Invalid flag: -${OPTARG}." >&2
            usage
            exit 2
            ;;
    esac
done

if [[ -z "$CONFIG" ]] && [[ -z "$ON" ]] && [[ -z "$OFF" ]] && [[ -z "$LIST" ]]; then
    echo "Missing -a, -w or -c argument." >&2
    exit 1
fi

if [[ -n "$CONFIG" ]]; then
    if [[ -n "$SSID" ]] && [[ -n "$PW" ]]; then
        NETWORK=$(wpa_passphrase "$SSID" "$PW")
        if [[ "$NETWORK" == network* ]]; then
            EXISTS=$(sudo grep -F "$SSID" "$WPA_CONFIG") 
            if [[ -n "$EXISTS" ]]; then
                echo "Wi-Fi Network already exist!" >&2
                exit 1
            else
                echo "Adding Wi-Fi Network"
                echo "$NETWORK" | sudo tee -a "$WPA_CONFIG"
            fi
        else
            echo "Failed to add Network!" >&2
            echo "$NETWORK" >&2
            exit 1
        fi
    else
        echo "You must provide the Wi-Fi details as: -s SSID -p PASSPHRASE." >&2
        exit 1
    fi
fi

HOSTAPD_STATUS="$(systemctl is-active hostapd.service)"

if [[ -n "$ON" ]] && [[ -n "$OFF" ]]; then
    echo "Combination not allowed." >&2
    exit 1
elif [[ -n "$ON" ]] && [[ "$HOSTAPD_STATUS" == 'inactive' ]]; then
    activate_ap
elif [[ -n "$OFF" ]] && [[ "$HOSTAPD_STATUS" != 'inactive' ]]; then
    deactivate_ap
else
    echo "The service hostapd is already ${HOSTAPD_STATUS}"
fi

if [[ -n "$LIST" ]]; then
    sudo cat "$WPA_CONFIG"
fi
