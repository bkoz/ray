#!/bin/bash

helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update
helm install kuberay-operator kuberay/kuberay-operator

echo
echo Waiting for the kuberay-operator pod.
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kuberay-operator --timeout=300s

# helm install raycluster kuberay/ray-cluster
helm install raycluster kuberay/ray-cluster --values=ray-cluster/values.yaml
kubectl get pods --show-labels
echo
echo Waiting for the ray cluster pods to become ready.
sleep 10
kubectl wait --for=condition=ready pod -l app.kubernetes.io/created-by=kuberay-operator --timeout=300s

