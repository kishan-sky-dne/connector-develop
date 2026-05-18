# """
# __author__ = "Sky UK Ltd"
# __copyright__ = Copyright © Sky CP Limited 2023.
# All rights reserved. No part of this work may be reproduced,
# stored in a retrieval system of any nature, or transmitted,
# in any form or by any means including photocopying
# and recording, without the prior written permission of Sky,
# the copyright owner.
# __licence__ = "subject to the terms of the licence with Sky UK Ltd'
# __version__ = "1.0"
# """
#!/usr/bin/env bash

set -e
echo "Installing yaml"
pip3 install PyYAML
echo "Running the script to update deployment.yaml"
python3 scripts/deployment.py


if [ "${CI_COMMIT_REF_NAME}" = "develop" ] || [ "${CI_COMMIT_REF_NAME}" = "test" ] || [ "${CI_COMMIT_REF_NAME}" = "stage" ] || [ "${CI_COMMIT_REF_NAME}" = "master" ]
then
  server=K8S_SERVER_${CI_COMMIT_REF_NAME^^}
  user_token=K8S_USER_TOKEN_${CI_COMMIT_REF_NAME^^}
  K8S_SERVER=${!server}
  K8S_USER_TOKEN=${!user_token}

else
  K8S_SERVER=${K8S_SERVER_DEVELOP}
  K8S_USER_TOKEN=${K8S_USER_TOKEN_DEVELOP}
fi


kubectl config set-cluster k8s --server="${K8S_SERVER}"
kubectl config set-credentials "${K8S_USER_NAME}" --token="${K8S_USER_TOKEN}"
kubectl config set-context default --cluster=k8s --user="${K8S_USER_NAME}"
kubectl config use-context default
echo "Applying the deployment.yaml to fluidcloud"
kubectl apply -f deployment.yaml


echo "Sleeping for 20 seconds"
sleep 20

echo "Copying the status of the deployment to output.json"
kubectl get -f deployment.yaml  -o json >> output.json

available=$(cat output.json | jq '.items[]|select(.kind=="Deployment").status.availableReplicas')
replicas=$(cat output.json | jq '.items[]|select(.kind=="Deployment").status.replicas')
ready_replicas=$(cat output.json | jq '.items[]|select(.kind=="Deployment").status.readyReplicas')

echo "Available: ${available}, Replicas: ${replicas}, readyReplicas: ${ready_replicas}"

echo "Verifying the state of the deployment"
if [ "${available}" = "${replicas}" ]; then exit 0; else exit 1; fi