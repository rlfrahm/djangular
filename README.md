My Drink Nation
===

## Setup

### Local

### Digital Ocean
1. Modify `/etc/nginx/sites-enabled/django`
2. Modify `/etc/init/gunicorn.conf`
3. Install git:
 * `sudo apt-get update`
 * `sudo apt-get install git`
 * Reference: https://www.digitalocean.com/community/tutorials/how-to-install-git-on-ubuntu-14-04
4. Clone repo to `/home/django/`
5. Create site specific settings file at `core/settings/site.py`
6. Upgrade Django to 1.8
 1. Remove system Django `rm -rf /usr/local/lib/python2.7/dist-packages/django`
 2. Install new Django `pip install django`
7. Install project dependencies using `pip install -r requirements.txt`
8. Migrate the database
9. Restart gunicorn `service gunicorn restart`

### Logs
* Gunicorn `/var/log/upstart/gunicorn.log`
* Nginx `/var/log/nginx/error.log`
