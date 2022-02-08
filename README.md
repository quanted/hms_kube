# HMS - Kubernetes

Hydrologic Micro-Services (HMS) is a water quality simulation and data provision service. The HMS technology stack is deployed and managed through 
Kubernetes, consisting of a full technology stack for web deployment. HMS consists of both a REST API for direct calls and a dynamic web user interface. The web stack contains the following components:
  - Django - hms_app
  - Angular 10 - hms_angular
  - Flask - hms_flask
  - Dask - hms_kube/dask
  - Nginx - hms_kube/hms_nginx
  - MongoDB - hms_kube/mongo
  - .NET 6 - hms
 
#### Kubernetes/Docker Builds
| Component | Deployment | Docker Image | Build Status |
| --------- | ---------- | ------------ | ------------ | 
| django | hms-django-deployment.yml | [quanted/hms_app](https://cloud.docker.com/u/dbsmith88/repository/docker/dbsmith88/hms-django) | ![Docker Build Status](https://img.shields.io/docker/cloud/build/dbsmith88/hms-django.svg) |
| flask | hms-flask-deployment.yml | [quanted/hms_flask](https://cloud.docker.com/u/dbsmith88/repository/docker/dbsmith88/hms-flask) | ![Docker Build Status](https://img.shields.io/docker/cloud/build/dbsmith88/hms-flask.svg) |
| dask | hms-dask-deployment.yml | [quanted/hms_kube/dask ](https://cloud.docker.com/u/dbsmith88/repository/docker/dbsmith88/hms-dask) | ![Docker Build Status](https://img.shields.io/docker/cloud/build/dbsmith88/hms-dask.svg) |
| nginx | hms-nginx-deployment.yml | [quanted/hms_kube/hms_nginx](https://cloud.docker.com/u/dbsmith88/repository/docker/dbsmith88/hms-nginx) | ![Docker Build Status](https://img.shields.io/docker/cloud/build/dbsmith88/hms-nginx.svg) |
| .NET 6 | hms-dotnetcore-deployment.yml | [quanted/hms](https://cloud.docker.com/u/dbsmith88/repository/docker/dbsmith88/hms_dotnetcore) | ![Docker Build Status](https://img.shields.io/docker/cloud/build/dbsmith88/hms_dotnetcore.svg) |

#### Requirements


##### Docker-Desktop (Windows)

Docker-Desktop is an alternative option for running a single-node kubernetes cluster. After installing Docker-Desktop, or updating to the latest version, turn Kubernetes on in Settings and restart docker-desktop. A new kubernetes context will be created 'docker-desktop' which can be used to run the stack.

To allow for the mounts, the mounted directories need to be specified or be a sub-directory of a directory which docker-desktop has access to 'Resources > File Sharing'. The compute resources which are specified are the max that the kubernetes cluster will have access to.
Depending on existing kubectl configurations, the new context may need to be set as current.
```commandline
kubectl config current-context
```
If 'docker-desktop' is not the current config, check to see if it is listed in the available contexts
```commandline
kubectl config get-contexts
```
if available, set 'docker-desktop' to the current context by
```commandline
kubectl config set-context docker-desktop
```
or
```commandline
kubectl config use-context docker-desktop
```
Now any kubectl will use the docker-desktop context, the kubernetes resources for hms can now be applied.
The order to apply the resources should be: ConfigMap, PersistentVolumes, PersistentVolumeClaims, Services, StatefulSet, Deployments, HPAs.

Or to apply all the kubernetes manifests for the application at once, run the following from the root of the repo:
```commandline
kubectl apply -f k8s\
```
To create the resources for the  kubernetes dashboard, run the following commands
```commandline
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.2.0/aio/deploy/recommended.yaml
kubectl proxy
```
The resources necessary for the dashboard are now running, and can be accessed at:
http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

The first time reaching the dashboard will prompt for a login token or key, to skip this step open the kubernetes-dashboard deployment for editing 
```commandline
kubectl edit deploy/kubernetes-dashboard -n kubernetes-dashboard
```
and add the following line under spec.containers.args after the others in the list of args:
```yaml
- --enable-skip-login
```
Those changes will automatically apply once the editing is completed and the yaml is valid. Then revisiting or reloading the dashboard will again prompt for a token/login but also have the option to skip.

Django and Dask have optional hostPath mounts which can be used for local code development and testing, code is mounted directly to the pod so no image rebuilds required (typically requires a pod restart).
To use these hostPaths make sure that the Volume and VolumeMount blocks are both uncommented. If the hostPath mounts are not used, Django and Dask will use the current code in the image being used (most likely the last commit to github on the main branch).

To access the running technology stack, we can access the open NodePort on hms-nginx that is specified to be port 31000. http://localhost:31000/hms will open up the web application, alternatively http requests can be made to the same base url via Postman or curl.
 
Resource metrics can also be tracked by deploying the metric-server
```commandline
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```
