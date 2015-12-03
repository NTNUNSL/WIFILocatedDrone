#!/bin/bash

airodump-ng wlan0 -c 1,1 2>> /dev/stdout | grep "Nick"

