import shutil

from pytest_redis import factories

redis_proc = factories.redis_proc(executable=shutil.which("redis-server"), port=1234)
redis = factories.redisdb("redis_proc")
