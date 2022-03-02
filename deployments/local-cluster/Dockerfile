# syntax=docker/dockerfile:1
FROM apollodorus/routines-base:v1 
WORKDIR /routines/routines

ENTRYPOINT celery -A cluster worker -l INFO 
