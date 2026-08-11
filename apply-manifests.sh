#!/bin/bash

envsubst < k8s/hms-configmap.yml | kubectl apply -f -
envsubst < k8s/hms-dask-scheduler-deployment.yml | kubectl apply -f -
envsubst < k8s/hms-dask-scheduler-service.yml | kubectl apply -f -
envsubst < k8s/hms-dask-worker-deployment.yml | kubectl apply -f -
envsubst < k8s/hms-dask-worker-hpa.yml | kubectl apply -f -
envsubst < k8s/hms-django-deployment.yml | kubectl apply -f -
envsubst < k8s/hms-django-service.yml | kubectl apply -f -
envsubst < k8s/hms-dotnet-deployment.yml | kubectl apply -f -
envsubst < k8s/hms-dotnet-service.yml | kubectl apply -f -
envsubst < k8s/hms-flask-deployment.yml | kubectl apply -f -
envsubst < k8s/hms-flask-service.yml | kubectl apply -f -
envsubst < k8s/hms-mongodb-service.yml | kubectl apply -f -
envsubst < k8s/hms-mongodb-sts.yml | kubectl apply -f -
envsubst < k8s/hms-nginx-deployment.yml | kubectl apply -f -
envsubst < k8s/hms-nginx-service.yml | kubectl apply -f -
