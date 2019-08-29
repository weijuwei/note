from kazoo.client import KazooClient
import json
zk = KazooClient(hosts="127.0.0.1:2181, 127.0.0.1:2182, 127.0.0.1:2183")
zk.start()
znode = {
  "hello": "world",
}
znode = json.dumps(znode)
znode = bytes(znode, encoding="utf-8")
zk.set("/test", znode)
