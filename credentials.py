import boto3


def get_credentials():
	USER_POOL_ID = 'us-east-1_o1VbRGfRz'
	APP_CLIENT_ID = '1oaud6tghpbha92nfo4vi6l0r5'
	APP_CLIENT_SECRET = '13ct9h4m2k9oq5hutg972s0kk9rte9gc273qotg9omqmulfivcu3'
	return USER_POOL_ID, APP_CLIENT_ID, APP_CLIENT_SECRET

