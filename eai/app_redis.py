import redis

class Redis:
    r = None

    @classmethod
    def _initialize(self):
        if self.r is None:
            self.r = redis.Redis(host='redis-15606.c299.asia-northeast1-1.gce.redns.redis-cloud.com',
                port=15606,
                password='ftlMBkEMtHHaxowQVpDoK8loYK3x9TtX'
            )
            try:
                if self.r.ping():
                    print("Redis Ready!")
            except redis.ConnectionError:
                print('Failed to connect to redis')
                self.r = None
    
    @classmethod
    def get(self):
        return self.r
    
