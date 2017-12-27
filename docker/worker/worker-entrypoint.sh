#!/usr/bin/env bash

until cd scapi
do
    echo "Waiting for django volume..."
done

sleep 10

celery worker -A scapi -l info
