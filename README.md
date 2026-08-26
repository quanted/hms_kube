**HMS Kube Local Setup**

0.  Remove any old HMS pods and volumes if initial setup

    a. Remove pods

      `kubectl delete -f k8s/ --force --grace-period=0`

    b. Remove PVCs and PVs

      `kubectl delete -f volumes-local.yml --force --grace-period=0`

2.  Pulling hms_kube

    a.  Using dev-local branch.

3.  Setting up environment

    a.  Create an .env file based off the template.env. The created .env
        file will stay outside source control / the repository.

    b.  Add EarthData credentials to .env file.

    c.  Set a path for the volumes.

        /run/desktop/mnt/host/d/hms_volume_data

    d.  In a Git bash terminal (anything with bash should work, Git bash
        is a common one for Windows), cd to the hms_kube repo.

    e.  Set the environment

        source .env

5.  Setting up PVs and PVCs

    a.  Run the volume setup script

        ./setup-volumes.sh

    b.  Check that the PVs and PVCs have been setup (it can take 30s or
        so for the PVCs to bind and may be in a pending state until
        then)

        kubectl get pv

        kubectl get pvc

6.  Running manifests

    a.  Run the script for running the pods that enables environment
        variable implantation

        ./apply-manifests.sh

    b.  For deleting the manifests, use the classic method

        kubectl delete -f k8s/
