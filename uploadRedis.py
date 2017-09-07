#Azure RedisDB
#Secondary Key: kEMDBWSkW41HVho6kVtPWk3iAFLtOynx6727nKb/H4g=
#Secondary Conn Str: watchful-pi-db.redis.cache.windows.net:6380,password=kEMDBWSkW41HVho6kVtPWk3iAFLtOynx6727nKb/H4g=,ssl=True,abortConnect=False
#Host Name: watchful-pi-db.redis.cache.windows.net

#!/usr/bin/env python
import time
import uuid
import redis

# app = Flask(__name__)
station_id = str(uuid.uuid1())
count = 0

wp_db_host = 'pub-redis-19350.us-east-1-1.1.ec2.garantiadata.com'
wp_db_key = 'ckXIkkG8ftEhK9NT'
wp_db_port = 19350
r = redis.Redis(host=wp_db_host,port=wp_db_port, db=0, password=wp_db_key)

def upload_heat_reading(heat):
    r.set('wp_id',station_id)
    r.set('wp_heat_reading',heat)

if __name__ == "__main__":
    r.get('wp_heat_reading')
    upload_heat_reading(50)
else:
    print("Retrieving data from Redis on PCF...")