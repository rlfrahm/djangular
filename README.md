Django / AngularJS Boilerplate (djangular) - THE INFOS
======================================================

This is meant as a starting point for your next Django / AngularJS project. Mostly what this consists of is common setup things you would do when starting your app. Some out of the box functionality/configuration that this adds are:

- Register / Login functionality and templates templates
- A user profile model that allows you to add custom attributes about a user
- AngularJs setup and ready to go
- A production ready settings configuration
- Django Rest Framework ready to go
- ... to be continued

Installation
------------

1. Fork this repository and then clone it locally
2. Create a `virtualenv`
3. Navigate to the root of this directory, and install the requirements `pip install -r requirements.txt`
4. Cope & paste `core/settings/default.site.py` to `core/settings/site.py`
5. Migrate the db `python manage.py migrate`
6. Run the server `python manage.py runserver`
