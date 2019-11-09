#!/usr/bin/python3

import random
import os

for i in range(1,253):
    ip1 = random.randint(1,253)
    ip2 = random.randint(1,253)
    #print(num)
    os.system('curl -H "X-Forwarded-For:%s.%s.42.%s" 192.168.1.254/soft/' %(ip1,ip2,i))
