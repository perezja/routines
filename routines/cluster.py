#!/usr/bin/env python3
import os
from celery import Celery

if "CELERY_BROKER_URL" not in os.environ:
    os.environ["CELERY_BROKER_URL"] = "amqp://localhost" 
if "CELERY_RESULT_BACKEND" not in os.environ:
    os.environ["CELERY_RESULT_BACKEND"] = "rpc://"
 
app = Celery('routines',
         broker=os.environ["CELERY_BROKER_URL"],
         backend=os.environ.get("CELERY_RESULT_BACKEND"),
         include=['tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

def make_celery():

    if "CELERY_BROKER_URL" not in os.environ:
        os.environ["CELERY_BROKER_URL"] = "amqp://localhost" 
    if "CELERY_RESULT_BACKEND" not in os.environ:
        os.environ["CELERY_RESULT_BACKEND"] = "rpc://"
 
    app = Celery('routines',
             broker=os.environ["CELERY_BROKER_URL"],
             backend=os.environ.get("CELERY_RESULT_BACKEND"),
             include=['tasks'],
             task_serializer='pickle',
             accept_content={'json', 'pickle'},
             result_accept_content={'json','pickle'})

    # Optional configuration, see the application user guide.
    app.conf.update(
        result_expires=3600,
    )
    return app

if __name__ == '__main__':

   
    # celery -A routines worker -l INFO  
    argv = [
        '-A', 'routines', 'worker', '-l', 'INFO'
        ]
    
#    app = make_celery()
    app.start()

