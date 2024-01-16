# Installation into Raspberry Pi device

This additional documentation deals with the deployment of the P1 logger into a Raspberry Pi device.

## Table of Contents

1. [Installation](#installation)
   1. [Install docker](#install-docker)
   2. [Install Access Point](#install-access-point)
   3. [Install portainer](#install-portainer)
2. [Default Configuration](#default-configuration)
3. [Networking](#networking)
   1. [Wi-fi Client](#wi-fi-client)
   2. [Reactivate Access Point](#reactivate-access-point)
   3. [Wired network](#wired-network)
4. [Remote backup](#remote-backup)
   1. [Prerequisites](#prerequisites)
   2. [Connection to the P1 reader](#connection-to-the-p1-reader)
   3. [Backup script](#backup-script)

## Installation

First, clone the repository and navigate to the `rpi-install` folder.

```bash
git clone https://github.com/ejpalacios/p1-reader-premises.git
cd p1-reader-premises/rpi-install
```

> `git` should be installed by default in your system. Otherwise, just run the command `sudo apt install git`. Likewise, an Internet connection is necessary.

The main installation script is `install.sh`. To see the available installation options use the switch `-h`.

```bash
$ ./install.sh -h
Install dependencies and tools

Arguments:
  -a | Install Access Point
  -c | Install DOCKER-COMPOSE
  -d | Install DOCKER
  -p | Install PORTAINER
  -h | Show this help
```

> Please note that you must log out and log in again for the group privileges to take effect.

### Install docker

For a normal operation, only `docker` and `docker-compose` are necessary, which can be added as

```bash
./install.sh -d
# log out and log in or reboot
./install.sh -c
```

> Note that after installing docker it is necessary to log in again for the changes to take place.

### Install Access Point

In many situations, the Smart Meter might be placed in a location with poor connectivity. Thus, a local Wi-Fi Access Point can be installed. **Note that this process will restart the device and disable the Wi-Fi client functionality**.

```bash
# add access point setup
./install.sh -a
```

> More details on how to connect to this access point or connect the data logger to your Wi-Fi network are provided in the [Networking](#networking) section.

### Install portainer

```bash
# add portainer instance
./install.sh -p
```

## Default configuration

If you are using a preconfigured version of the data logger the following defaults are used:

- Access point Wi-Fi Networking:
  - Configuration: Access Point with static IP `192.168.10.1`
  - SSID: `smartmeter`
  - passphrase: `premises-fwo`
- Ethernet Networking:
  - Configuration: DHCP with fallback static IP `192.168.11.1`
- Visualisation:
  - user: `admin`
  - password: `admin`

## Networking

By default, the data logger configures itself as an Wi-Fi Access point with the defaults indicated in the Section [Default configuration](#default-configuration).
However, it is possible to join the device to your local network using either Ethernet or Wi-Fi.

To edit the configuration, it is necessary to log into the device using the provided credentials. This can be done by

- Connecting the Raspberry Pi to a HDMI monitor and a keyboard and using the local terminal.
- Connecting remotely using SSH. On windows, you can use a client such as [PuTTY](https://putty.org/). Note that depending on the situation the IP address of the device will vary.
  - Connected to Access Point: `192.168.10.1` (Default)
  - Ethernet PC to Device: `192.168.11.1`. See Section [Wired Network](#wired-network)
  - Wi-Fi Client: Need to be determined. See Section [Wi-Fi Client](#wi-fi-client)

> In some situations, it might be possible to use the hostname of the data logger instead of the IP address. The hostname is printed on the external label on the device (e.g., `hems-1`).

### Wi-Fi Client

This configuration enables the integration of the data logger into an existing Wi-Fi Network.
Starting from the default Access Point configuration, we can connect to the device using SSH as below. Please change the IP address in other case.

```bash
ssh pi@192.168.10.1
```

After introducing our password, we need to navigate to the main source code folder:

```bash
cd p1-reader-premises/rpi-install
```

Here, the script `network.sh` will facilitate the configuration process. Its options are:

```bash
$ ./network.sh -h
Usage:
-a: Activate the Access Point
-c: Configure new Wi-Fi Network
    -s: SSID of the network
    -p: Passphrase
-w: Activate the Wi-Fi Network
```

The configuration of a new Wi-Fi network connection is a two step process.
First, the Wi-Fi details must be added.

```bash
./network.sh -c -s "MY_SSID" -p "MY_PASSWORD"
```

Here you need to replace `MY_SSID` with the name of the Wi-Fi network and `MY_PASSWORD` with the passphrase. Note that if the name contains blank spaces it must be surrounded by double quotes, e.g., "My network".

If you want to check that the network has been successfully added, this can be done by editing the configuration file. You can edit this file using the command below.

```bash
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

> Note that the configuration command adds the original non-hashed password as a comment in the `wpa_supplicant.conf` file. Feel free to remove this line to keep the password secret.

Once the new Wi-Fi network has been added. The data logger can be transfer to the Wi-Fi client configuration with the switch `-w`.

```bash
./network.sh -w
```

This process will reboot the device. On boot, it will attempt to connect to the provided Wi-Fi network.
In most home networks, the DHCP service of the router will assign a dynamic IP to the device. However, you should be able to access the device by using the hostname indicated on the label.

In case the Name server does not recognise the hostname, you can learn the new IP in two ways:

1. Log into your router and find the IP assigned to the raspberry pi.
2. Connect the device to a HDMI monitor and a keyboard and issue the command:

```bash
ifconfig wlan0 | grep "inet"
```

The new IP assigned will be under after the label `inet`

### Reactivate Access Point

If at any point you might like to reactivate the Hotspot, simply log into the data logger via SSH.

```bash
ssh pi@HOSTNAME # Or IP Address assigned by the Home router
```

Navigate to the source code folder and run the `network.sh` script with the switch `-a`.

```bash
./network.sh -a
```

The device will reboot and start up with the default network configuration indicated in Section [Default configuration](#default-configuration)

### Wired network

An Ethernet interface is also activated on the device and can be used to connect the data logger to your home network with no additional configuration.
The IP assignation and access procedure is similar to the one described for the Wi-Fi client situation.

An additional feature of this Ethernet connection is to act as a backup interface if the Wi-Fi is misconfigured.
To use this interface, first connect your PC directly to the Raspberry Pi using an Ethernet cable.

Then, configure your PC to have an static IP as follows. In Windows, this configuration can be added under "Ethernet Properties" → "Networking" → "Internet Protocol Version 4 Properties"

- IP Address: 192.168.11.2
- Subnet mask: 255.255.255.0
- Default gateway: 192.168.11.1

After this, you should be able to log into the device via SSH.

```bash
ssh pi@192.168.11.1
```

## Remote Backup

Although the backup process is document in the main [README](https://github.com/ejpalacios/p1-reader-premises/blob/main/README.md#data-back-up-and-restore) file, we outline here the process to remotely backup the measurements from the Raspberry Pi P1 logger into a main PC.

### Prerequisites

Please clone the repository into the main PC.

```bash
git clone https://github.com/ejpalacios/p1-reader-premises.git
```

Likewise, make sure `poetry` is installed in the main PC as indicated in the [README](https://github.com/ejpalacios/p1-reader-premises/blob/main/README.md#prerequisites)

### Connection to the P1 reader

The connection to the P1 reader depends on the active interface. We need to join the main PC to the same network as the P1 reader and determine the `IP`

- Access Point:
  1. Connect the main PC to the Wi-Fi network create by the P1 logger
  2. Default `IP=192.168.10.1`
- Wi-Fi:
  1. Connect the main PC to the same network as the P1 logger.
  2. Determine the IP address assigned by your router to the P1 logger.
- Wired network:
  1. Connect the main PC via an Ethernet cable to the P1 logger and configure static IP. See [Wire network](#wired-network)
  2. Default `IP=192.168.11.1`

### Backup script

Run the backup script from the main PC by inserting the IP and EAN for the meter in the command below.

**This process can take several hours depending on the data stored in the DB. Do not disconnect the main PC from the network above or turn on the P1 reader throughout the process**.

```bash
poetry run python ./utils/backup.py -H {IP} -i {EAN} --all
```

> Note that if some of the default parameters for the database were change additional arguments will have to be provided as indicated in main [README](https://github.com/ejpalacios/p1-reader-premises/blob/main/README.md#data-back-up-and-restore).
