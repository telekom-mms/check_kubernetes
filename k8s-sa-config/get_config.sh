#!/bin/bash

API_SERVER="https://localhost:6443"
SERVICEACCOUNT_NAME=$(kubectl get sa | grep icinga | awk '{ print $1 }')
SECRET_NAME=$(kubectl get secrets | grep "${SERVICEACCOUNT_NAME}-token" | awk '{ print $1 }')

if [[ ${SERVICEACCOUNT_NAME} == "" ]]; then
    >&2 echo "Service account not found!"
    exit 1
else
    >&2 echo "Found icinga Service Account: ${SECRET_NAME}"
fi

CA_CERT=$(kubectl get secret/"${SECRET_NAME}" -o jsonpath='{.data.ca\.crt}')
SA_TOKEN=$(kubectl get secret/"${SECRET_NAME}" -o jsonpath='{.data.token}' | base64 --decode)
NS=$(kubectl get secret/"${SECRET_NAME}" -o jsonpath='{.data.namespace}' | base64 --decode)

echo "
apiVersion: v1
kind: Config
clusters:
- name: default-cluster
  cluster:
    certificate-authority-data: ${CA_CERT}
    server: ${API_SERVER}
contexts:
- name: default-context
  context:
    cluster: default-cluster
    namespace: ${NS}
    user: default-user
current-context: default-context
users:
- name: default-user
  user:
    token: ${SA_TOKEN}
"
