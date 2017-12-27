# Voyer Indentity API
## authentication and user management for the secure cloud platform

## requirements
* python 3.6.1+
* [virtualenv](https://virtualenv.pypa.io/en/stable/installation/)
* [django-rest-knox(mega-secure)](https://james1345.github.io/django-rest-knox/installation/)
* [django-rest-framework-jwt(semi-secure)](http://getblimp.github.io/django-rest-framework-jwt/)

## getting started
```shell
cd scapi
virtualenv -p `which python3.6` ./env
source ./env/bin/activate
pip install -r py-requirements/base.txt
```
## initialise your local database
```shell
cd scapi
python manage.py migrate
```
Create a local superuser with say username ```admin``` and password ```password123``` for example
```shell
python manage.py createsuperuser
```
## running the service

```py
python manage.py runserver
```

## Documentation
### Swagger docs
browse to [http://localhost:8000](http://localhost:8000)

# example usage:
## login
```
curl -XPOST -H 'Accept: application/json; indent=4' -u <username>:<password> http://127.0.0.1:8000/api/auth/login/
```
```json
{
    "user": {
        "username": "<username>",
        "first_name": "",
        "last_name": ""
    },
    "token": "d626c65781c4530c5e63d6da93a3e1b515a36948314ce4aad65162f4f89382d4"
}
```
## logout
```
curl -XPOST -H 'Authentication: Token <insert token allocated from /login endpoint>' http://127.0.0.1:8000/api/auth/logout/
```
