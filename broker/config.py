from os import environ as env

RECAPTCHA_SECRET_KEY = env.get('RECAPTCHA_SECRET')
RECAPTCHA_SITE_VERIFY_URL = env.get('RECAPTCHA_URL')
SLACK_KEY = env.get('SLACK_KEY')

