#!/bin/bash

echo "Setting up PVs and PVCs."
envsubst < volumes-local.yml | kubectl apply -f -
echo "Done."