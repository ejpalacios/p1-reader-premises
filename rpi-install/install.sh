#!/bin/bash

BACKUP_PATH=~/.network_backup
DHCPCD_CONFIG_FILE=/etc/dhcpcd.conf
DNSMASQ_CONFIG_FILE=/etc/dnsmasq.conf

function usage() {
    echo "Install dependencies and tools"
    echo
    echo "Arguments:"
    echo "  -a | Install Access Point"
    echo "  -c | Install DOCKER-COMPOSE"
    echo "  -d | Install DOCKER"
    echo "  -p | Install PORTAINER"
    echo "  -h | Show this help"
}

function update() {
    sudo apt update && sudo apt full-upgrade -y
}

function install_docker() {
    echo "Installing docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -ag docker "$USER"
    docker version
}

function install_docker_compose() {
    echo "Installing docker-compose..."
    venv/bin/pip3 install docker-compose --user
}

function install_portainer() {
    echo "Installing portainer..."
    docker volume create portainer_data
    docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
}


function install_ap(){
    # Install Access Point
    echo "Installing hostapd and dnsmasp..."
    sudo apt install -y hostapd dnsmasq

    # Backup configuration files
    echo "Backing up configuration files"
    mkdir "$BACKUP_PATH"
    sudo mv "$DHCPCD_CONFIG_FILE" "${BACKUP_PATH}/"
    sudo mv "$DNSMASQ_CONFIG_FILE" "${BACKUP_PATH}/"

    # Enable hostpad
    echo "Enabling hostpad service..."
    sudo systemctl unmask hostapd.service

    ./network.sh -a
}

UPDATE=
DOCKER=
COMPOSE=
AP=
PORTAINER=

while getopts ":acdfph" arg
do
    case ${arg} in
        a) 
            UPDATE='true'
            AP='true'
            ;;
        c) 
            COMPOSE='true'
            ;;
        d)  
            UPDATE='true'
            DOCKER='true'
            ;;
        p) 
            PORTAINER='true'
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
            echo "$0: Invalid flag: -${OPTARG}." >&2
            usage
            exit 2
            ;;
    esac
done

if [[ -n "$UPDATE" ]]; then
    update
fi

if [[ -n "$DOCKER" ]]; then
    install_docker
fi

if [[ -n "$AP" ]]; then
    install_ap
    echo "Rebooting system..."
    echo "After boot you can connect to the SSID=smartmeter"
    echo "The device can be accessed on the IP=192.168.10.1"
    echo ""
    sudo reboot
fi

if [[ -n "$COMPOSE" ]]; then
    create_virtual_env
    install_docker_compose
fi

if [[ -n "$PORTAINER" ]]; then
    install_portainer
fi
