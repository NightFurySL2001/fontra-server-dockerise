# fontra-server-dockerise

Configure the following files:
* `docker-compose.yml`: database username and password, also register invitation key
* `robocjk-settings`: database username and password
* `nginx/nginx-selfsigned.*`: SSL certificate for internal SSL verification, and also used for accessing the Django admin panel
* `git-ssh`: standard `.ssh` folder containing SSH credentials to push to a remote git repo for version control
* `rcjk-src`: optional, used for importing external `.rcjk` file into service
then start with `docker compose up -d`.

## Database

Official support from `django-robo-cjk` is MySQL. However PostgreSQL will work too:
* uncomment PostgreSQL and comment MySQL in `docker-compose.yml`;
* switch the `DATABASE_ENGINE` to `django.db.backends.postgresql` in `robocjk-settings`;
* change the port numbers in `robocjk-settings` and `docker-compose.yml`;
* add `psycopg2-binary` in `django-robo-cjk/requirements.txt`;
* edit the `fontra-register/app.py` logic <sub>(sorry i forgot lol)<sub>

## Ports

* 8000: user page (HTTPS)
* 18089: Django control (HTTPS)
* 3306: MySQL database
* 5432: PostgreSQL database
* 5000: register site (optional, available under `localhost:5000/register`)

Or if you want to host on one port only, use nginx with `global-nginx.conf` which will combine the Fontra site, admin panel (`localhost/admin`) and register page (`localhost/register`) in one exposable port.

## Admin control

You may want to exec into the server container to run Django commands through `python manage.py`.

A common one is `python manage.py export_rcjk`. If git fails for the first time, manually clone the repo in `/var/lib/.rcjks/[project name]` in the server container. Remember to add your git credentials in `git-ssh` folder for this to work.
