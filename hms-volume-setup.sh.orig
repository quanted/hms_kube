#!/bin/bash
echo "Starting HMS volumes setup"

kubectl exec deploy/oms-shell -- /bin/bash -c "mkdir /tmp/hms"

echo "Updating files from s3 bucket"
kubectl exec deploy/oms-shell -- /bin/bash -c "cd /tmp/hms ; rm -rf app-data"
kubectl exec deploy/oms-shell -- /bin/bash -c "aws s3 cp s3://qed-stg/hms /tmp/hms --recursive"
kubectl exec deploy/oms-shell -- /bin/bash -c "cd /mnt/hms-dotnetcore-appdata; rm -r *"
kubectl exec deploy/oms-shell -- /bin/bash -c "cp -rf /tmp/hms/* /mnt/hms-dotnetcore-appdata"
kubectl exec deploy/oms-shell -- /bin/bash -c "rm -rf /tmp/hms/"
kubectl exec deploy/oms-shell -- /bin/bash -c "mkdir /mnt/mongodb-pvolume/hms/"

echo "Completed updates from s3 bucket"
echo "Completed QED code update"
