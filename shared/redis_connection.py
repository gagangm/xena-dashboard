from django_redis import get_redis_connection

def get_connection(con):
	redis = get_redis_connection(con)
	return redis