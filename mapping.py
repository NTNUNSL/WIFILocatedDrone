# -*- coding: UTF-8 -*-
'''
python 2.6
raspberry pi with 2014-01-07-wheezy-raspbian

RSSI/WiFi Signal Receiver

1. 必須安裝 tcpdump, airmon-ng
2. 第二張 WiFi card (wlan1) 必須在 monitor mode 狀態
3. 收集 120 個 packets 後停止

'''

import os
import subprocess as sub
import time
import re
import sys
import signal

if __name__ == '__main__':
    # initial mon
    is_mon_on = True
    S3_mac = '88:30:8a:7d:96:72'	# phone's mac address
    pkt_max = 120					# pkt in each location
    
    
    filename = ''
    if len(sys.argv) == 3:
        # command: python [program_name.py] [path.No.] [location(m)]
        path_number = str(sys.argv[1])
        location = str(sys.argv[2])
        filename = 'path{0}.{2}m.{3}'.format(path_number,location,'S3_data')
    if len(sys.argv) == 2:
        # command: python [program_name.py] [location(m)]
        location = str(sys.argv[1])
        filename = '{0}m.{1}'.format(location,'S3_data')
    
    # init mon0
    if is_mon_on:
        os.system('sudo airmon-ng check kill')
        os.system('sudo airmon-ng stop mon0')
        os.system('sudo airmon-ng start wlan1 up')
        time.sleep(10)
    
	# recording RSSI
    start_time = time.clock()
    tcpdump = sub.Popen(('sudo', 'tcpdump', '-e', '-i', 'mon0', '-vv' ), stdout=sub.PIPE)
    pkt_count = 0
    max_rssi = -127
    for pkt in tcpdump.stdout:  
        match = re.search('^(\d+):(\d+):(\d+).(\d+)(.*)-(\d+)dB(.*)(SA:|TA:)(.+?) (.*)$', pkt)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            second = float(match.group(3))
            minisec = float('0.'+str(match.group(4)))
            rssi = int(match.group(6))*-1
            mac = str(match.group(9))
            if mac == S3_mac:
                if rssi > max_rssi:
                    max_rssi = rssi
                pkt_count += 1
                file = open(filename,'a')
                #data = '{0}:{1}:{2} {3}\n'.format(hour,minute,second+minisec,rssi)
				data = '{0}\n'.format(rssi)
                file.write(data)
                file.close()
                if pkt_count > pkt_max:
                    break
    os.kill(tcpdump.pid, signal.SIGINT)
    time.sleep(2)
    print 'max rssi: ',max_rssi
    print 'time: ', time.clock()-start_time
