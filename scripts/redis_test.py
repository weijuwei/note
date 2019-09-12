#!/usr/bin/python3

import redis
import sys

if len(sys.argv) <=1:
    print("Usage: ./python [HASHKEY]")
    sys.exit()
else:
    hashkey = sys.argv[1]


def redis_hash_del(hashkey):

	rd = redis.Redis(host='192.168.1.201',port=6379,db=0)

	if rd.exists(hashkey):
		hashkey_all = rd.hkeys(hashkey)
		for k in range(len(hashkey_all)):
			rd.hdel(hashkey,hashkey_all[k])
		print(k)
	else:
		print("key not exists")

if __name__ == "__main__":
	redis_hash_del(hashkey)
