**HMS Kube Local Setup**

1.  Pulling hms_kube

    a.  Using dev-local branch.

2.  Setting up environment

    a.  Create an .env file based off the template.env. The created .env
        file will stay outside source control / the repository.

    b.  Add EarthData credentials to .env file.

    c.  Set a path for the volumes.

        i.  Example: /run/desktop/mnt/host/d/hms_volume_data

    d.  In a Git bash terminal (anything with bash should work, Git bash
        is a common one for Windows), cd to the hms_kube repo.

    e.  Set the environment (Note: "\$" is just there to imply a command
        and is not a part of the command)

        i.  \$ source .env

3.  Setting up PVs and PVCs

    a.  Run the volume setup script

        i.  \$ ./setup-volumes.sh

    b.  Check that the PVs and PVCs have been setup (it can take 30s or
        so for the PVCs to bind and may be in a pending state until
        then)

        i.  \$ kubectl get pv

        ii. \$ kubectl get pvc

4.  Running manifests

    a.  Run the script for running the pods that enables environment
        variable implantation

        i.  \$ ./apply-manifests.sh

    b.  For deleting the manifests, use the classic method

        i.  \$ kubectl delete -f k8s/