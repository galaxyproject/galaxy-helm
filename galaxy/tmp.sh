mkdir -p /tmp/k8s/volumes/ && cd "$_"
curl https://galaxy-helm-dev.s3.amazonaws.com/galaxy-db.tar.gz | tar -xz - && cd - && \
kubectl create -f postgres-pv.yaml
