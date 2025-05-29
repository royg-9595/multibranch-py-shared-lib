#!/bin/sh
python manage.py migrate
python manage.py runserver 0.0.0.0:8000 #default runserver works on localhost:8000, so we are changing here inside the container
