## EKS cluster
You'll have to configure access to the cluster with eksctl and kubectl.
(more info coming.)
All commands have to be run from gamestop/deploy root directory

### Creating the EKS cluster
eksctl create cluster -f cluster.yaml


### Install the application using Helm
helm install flkafka ./


### Uninstalling the application
helm delete flkafka


### Delete the EKS cluster
kubectl delete cluster -f cluster.yaml

