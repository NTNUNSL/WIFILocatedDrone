#!/bin/bash

airodump-ng wlan0 -c 11,11 2>> /dev/stdout | grep "Nick"

