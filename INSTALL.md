# Installation Instructions 
## Pre-Requisites
- Monitoring-User (nagios) with Home-Dir (/home/nagios) is setup 
- NRPE is working correctly 

## Install from release 
### download release versions (for release 1.2.1) 
```bash
[nagios@host ~]$ cd /home/nagios
[nagios@host nagios]$ mkdir check_kubernetes
[nagios@host nagios]$ cd check_kubernetes
[nagios@host check_kubernetes]$ RELEASE_URL="https://github.com/T-Systems-MMS/check_kubernetes/releases/download/"
[nagios@host check_kubernetes]$ VERSION="v1.2.1"
[nagios@host check_kubernetes]$ wget ${RELEASE_URL}/${VERSION}/check_pods
[nagios@host check_kubernetes]$ wget wget ${RELEASE_URL}/${VERSION}/check_nodes
[nagios@host check_kubernetes]$ chmod 0750 check_pods check_nodes
```

## Install from Source 
### Python environment
The following steps have to be executed as Nagios/NRPE user (user who will run the checks).

#### venv setup and clone
```bash
[nagios@host ~]$ cd /home/nagios
[nagios@host nagios]$ python3 -m venv k8s_mon_venv
[nagios@host nagios]$ source k8s_mon_venv/bin/activate
[nagios@host nagios]$ git clone https://github.com/T-Systems-MMS/check_kubernetes.git
[nagios@host nagios]$ cd check_kubernetes
[nagios@host check_kubernetes]$ pip install -r requirements.txt 
```

## Kubernetes Service Account Setup 
All files shown here can be found in folder k8s-sa-config. 

### Service Account - 00_service_account.yaml
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: icinga-monitoring-sa
```

### ClusterRole - 01_clusterrole.yaml
```yaml
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: icinga-monitoring
rules:
- apiGroups: [""]
  resources: ["pods", "nodes"]
  verbs: ["get", "watch", "list"]
```

### ClusterRoleBinding - 02_clusterrolebinding.yaml
```yaml
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: icinga-monitor-pods
subjects:
- kind: ServiceAccount
  name: icinga-monitoring-sa
  namespace: default
roleRef:
  kind: ClusterRole
  name: icinga-monitoring
  apiGroup: rbac.authorization.k8s.io
```

## Kubernetes - Get kube-config for service Account 
### get_config.sh
We assume here that the script is executed on a master node. If this is not the case you
must change `API_SERVER` here. <br>
If you've used another service account name also change `SERVICEACCOUNT_NAME` to reflect the change. 

```bash
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
```

To generate the kube-config for the service account just call it and redirect the output to a location that is 
accessible for nagios/nrpe.
The user running the script must have the kubernetes connection and privileges to run kubectl commands 
on cluster level ex. root   

```bash
[root@host ~]# chmod u+x get_config.sh
[root@host ~]# ./get_config.sh > /home/nagios/kube-config
[root@host ~]# chown nagios.nagios /home/nagios/kube-config
[root@host ~]# chmod 0600 /home/nagios/kube-config 
```

## Testing the newly created service account 
You can test service account configuration by running the check manually.

```bash 
[nagios@host ~]$ cd /home/nagios/
[nagios@host nagios]$ ls
bin  check_kubernetes  k8s_mon_venv  kube-config
[nagios@host nagios]$ cd check_kubernetes/
[nagios@host check_kubernetes]$ ./check_nodes --kube-config ../kube-config
NODES OK - problem_nodes is 0 | all_nodes=5;;;0 problem_nodes=0;1;2;0
[nagios@host check_kubernetes]$ ./check_pods --kube-config ../kube-config
PODS OK - 0 Pods Pending, 28 Pods Running, 0 Pods Succeeded, 0 Pods Failed, 0 Pods Unknown | Failed=0;;;0 Pending=0;;;0 Running=28;;;0 Succeeded=0;;;0 Unknown=0;;;0
[nagios@host check_kubernetes]$
```

# Troubleshooting 
## Error: Hostname doesn't match
If you get an exception like this: <br>
```
NODES UNKNOWN: urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='localhost', port=6443): Max retries exceeded with url: /api/v1/nodes (Caused by SSLError(SSLCertVerificationError("hostname 'localhost' doesn't match either of '<redacted>', 'kubernetes', 'kubernetes.default', 'kubernetes.default.svc', 'kubernetes.default.svc.cluster.local', '<redacted>', '<redacted>'")))
```
check the "server" line under "cluster" ``kube-config`` and replace localhost with one of names in the error message.
<br>