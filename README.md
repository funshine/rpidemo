# rpidemo
some demo for raspberry pi

## Install rpi

grab the raspbian image

use etcher to flash image to tf/sd

mount tf it will show boot

## Enable SSH

```shell
cd /Volume/boot
touch ssh
```

## Setup

```shell
sudo rasp-config
```

almost enable every interface.

set locale/timezone/password/hostname

`vim ~/.bashrc` add `exprot LC_ALL=C`

## SD card

Compatible sd card refer to [RPi_SD_cards](https://elinux.org/RPi_SD_cards)
