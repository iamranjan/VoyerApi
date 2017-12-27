# Voyer Indentity API
## authentication and user management for the secure cloud platform

## requirements
* python 3.6.1+
* [virtualenv](https://virtualenv.pypa.io/en/stable/installation/)
* [django-rest-knox(mega-secure)](https://james1345.github.io/django-rest-knox/installation/)
* [django-rest-framework-jwt(semi-secure)](http://getblimp.github.io/django-rest-framework-jwt/)

## getting started
```shell
git clone https://git.saharalab.net/pants/sc-identity
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
## setup rabbitmq for jobs api
```
brew install rabbitmq
/usr/local/sbin/rabbitmq-server -detached
/usr/local/sbin/rabbitmqctl add_user jobs jobs
/usr/local/sbin/rabbitmqctl add_vhost /jobs
/usr/local/sbin/rabbitmqctl set_permissions -p /jobs jobs ".*" ".*" ".*"
```
## Start jobs celery process
```
change into root of project (where manage.py is)
MONITORING: $ celery -A scapi flower
WORKER: $ celery -A scapi worker -l info
```

## kafka debugging/development
```
initiate ssh VPN/proxy into environment via [sshuttle](http://sshuttle.readthedocs.io/en/stable/index.html):
$ sshuttle --dns -vNHr bebsworth@linux-mgmt.saharalab.net:33001
change your local nameserver to 192.168.71.201
then we tunnel to a kafka node:
$ ssh -N -L 9091:localhost:9091 root@demo-sc-kafka-01.mgmt.pants.net

Now we can test kafka message consumption etc:

python
Python 3.6.2 (default, Jul 17 2017, 16:44:45) 
[GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.42)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> 
>>> 
>>> from kafka import KafkaConsumer
>>> consumer = KafkaConsumer('demo',auto_offset_reset='smallest',bootstrap_servers='localhost:9091')

if no error occurs then you've got a working connection to the kafka broker.

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
# TODO
* Add python based test cases to demonstrate functionality
* Add models and corresponding serialisers for mapped user S3 credentials
* Containerise project
  * Dockerfile
  * docker-compose.yml
* Add deployment scripts for local and prod
* Add instructions for getting started with rabbitmq & celery
## References
[ 1 ] (https://github.com/Seedstars/django-react-redux-base)
[ 2 ] (https://github.com/geezhawk/django-react-auth)
[ 3 ] (https://github.com/James1345/django-rest-knox)
[ 4 ] (https://github.com/GetBlimp/django-rest-framework-jwt)
[ 5 ] (http://docs.celeryproject.org/en/latest/getting-started/brokers/rabbitmq.html)
