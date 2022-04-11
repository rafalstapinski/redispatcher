import shutil

from pytest_redis import factories

print(f"\n\n\n{shutil.which('redis-server')=}\n\n\n")

redis_proc = factories.redis_proc(executable=shutil.which("redis-server"), port=1234)
redis = factories.redisdb("redis_proc")
