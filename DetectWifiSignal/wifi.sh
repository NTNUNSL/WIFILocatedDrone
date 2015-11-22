#!/bin/bash

airodump-ng wlan0 2>> /dev/stdout | grep "Nick"
