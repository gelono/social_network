"Social Network".

This is a REST API implementation using Django. API documentation is available at localhost:8000/swagger.

Several endpoints are implemented here to receive and manage data depending on user rights.
Users can register, post, like and unlike posts.
The administrator can view aggregate statistics on likes and track the time of the user’s last visit and access to the resource.
User authentication is performed using a token.

It also implements a CI element with automatic code checking - flake8 and unit tests.

After starting the application, create a superuser with the command: python manage.py createsuperuser.

To run the project use the following commands:

Install requirements:
```shell
pip install requirements.txt
```
Run migrations:
```shell
python manage.py migrate
```
Run server:
```shell
python manage.py runserver
```
