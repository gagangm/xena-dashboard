set -v
export DJANGO_SETTINGS_MODULE=xena.production_settings
git pull
kill -HUP `ps aux | grep emperor | grep -v grep | awk '{print $2}'`