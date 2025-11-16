# Suggested Addition to README.md

Add this section after the "Running Galaxy locally in a dev environment" section and before "Dependency charts".

---

## Gateway API Support (Alternative to Nginx Ingress)

The Galaxy Helm chart supports **Gateway API** as a modern alternative to traditional Ingress resources. Gateway API is the successor to Kubernetes Ingress and is recommended for new deployments.

### Prerequisites for Gateway API

1. **Kubernetes 1.27+** with Gateway API CRDs installed:
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.0.0/standard-install.yaml
   ```

2. **Gateway Controller** - Choose one of the following:

   **Option A: Istio (Recommended)**
   ```bash
   curl -L https://istio.io/downloadIstio | sh -
   cd istio-*
   ./bin/istioctl install --set profile=default -y
   ```

   **Option B: Kong Gateway**
   ```bash
   kubectl apply -f https://github.com/Kong/kubernetes-ingress-controller/releases/download/v3.0.0/all-in-one-dbless.yaml
   ```

   **Option C: Envoy Gateway**
   ```bash
   helm install eg oci://docker.io/envoyproxy/gateway-helm --version v1.0.0 -n envoy-gateway-system --create-namespace
   ```

### Installing with Gateway API

To install Galaxy using Gateway API instead of traditional Ingress:

```bash
# Create a values file for Gateway API
cat > galaxy-gateway-values.yaml <<EOF
gateway:
  enabled: true
  gatewayClassName: istio  # or kong, envoy-gateway
  hostname: "galaxy.example.com"
  tls:
    enabled: true
    certificateRef: "galaxy-tls-cert"

ingress:
  enabled: false  # Disable traditional Ingress
EOF

# Install Galaxy with Gateway API
helm install -n galaxy my-galaxy galaxy/ \
  -f galaxy-gateway-values.yaml \
  --set persistence.accessMode="ReadWriteOnce"
```

### Using an Existing Shared Gateway

For multi-tenant environments with a cluster-wide Gateway:

```bash
helm install -n galaxy my-galaxy galaxy/ \
  --set gateway.enabled=true \
  --set gateway.existingGateway=shared-gateway \
  --set gateway.existingGatewayNamespace=istio-system \
  --set ingress.enabled=false
```

### Migration from Nginx Ingress

For detailed migration instructions, see [GATEWAY_API_MIGRATION.md](GATEWAY_API_MIGRATION.md).

Quick migration steps:
1. Install Gateway API CRDs and Gateway controller
2. Update values: `gateway.enabled: true`, `ingress.enabled: false`
3. Perform `helm upgrade`
4. Verify routing with `kubectl get httproute -n galaxy`

### Supported Gateway Implementations

| Implementation | Status | Use Case |
|----------------|--------|----------|
| Istio | ✅ Recommended | Production deployments, advanced traffic management |
| Kong Gateway | ✅ Supported | API management, plugins, rate limiting |
| Envoy Gateway | ⚠️ Experimental | Newer projects, lighter weight |

---

**Note:** The traditional Nginx Ingress Controller is still supported for backward compatibility, but Gateway API is recommended for new deployments as Nginx Ingress is being deprecated.
