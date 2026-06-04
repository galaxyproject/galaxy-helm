# Gateway API Guide

Galaxy Helm chart supports **Gateway API** as a modern, standardized alternative to Kubernetes Ingress for routing traffic to Galaxy deployments.

## Overview

Gateway API is the successor to Kubernetes Ingress, providing:
- **Standardization**: Broad vendor support across Gateway implementations
- **Advanced routing**: Traffic splitting, header manipulation, retry policies
- **Role separation**: Clear boundaries between infrastructure (Gateway) and application (HTTPRoute)
- **Multi-tenancy**: Support for shared Gateways across multiple applications

The Galaxy chart supports **any** Gateway API v1+ implementation and can work in three modes:
1. **Chart-managed Gateway** - Chart creates its own Gateway resource
2. **Existing Gateway** - Use a cluster-wide shared Gateway
3. **Default Gateway** - Rely on Gateway API v1.4+ default Gateway attachment

## Quick Start

### Prerequisites

1. **Kubernetes 1.27+** with Gateway API CRDs installed. Choose one method:

   **Option A: Check if already installed** (many clusters include these):
   ```bash
   kubectl api-resources | grep gateway.networking.k8s.io
   # If found, you can skip CRD installation
   ```

   **Option B: Via galaxy-deps** (recommended for dev/test):
   ```bash
   helm install galaxy-deps galaxy-deps/ --set gateway.deploy=true
   ```

   **Option C: Manual installation** (recommended for production):
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.0.0/standard-install.yaml
   ```

2. **Gateway Controller** installed (choose one):
   - **Istio**: `istioctl install --set profile=default`
   - **Cilium**: Follow [Cilium Gateway API guide](https://docs.cilium.io/en/stable/network/servicemesh/gateway-api/gateway-api/)
   - **Traefik**: `helm install traefik traefik/traefik --set gatewayAPI.enabled=true`
   - **Kong**: Follow [Kong Gateway API installation](https://docs.konghq.com/kubernetes-ingress-controller/)
   - **Nginx Gateway Fabric**: Follow [NGF installation guide](https://docs.nginx.com/nginx-gateway-fabric/)

### Enable Gateway API

```yaml
# values.yaml
gateway:
  enabled: true
  gatewayClassName: istio  # or cilium, traefik, kong, nginx
  hostname: "galaxy.example.com"
  
ingress:
  enabled: false  # Disable traditional Ingress
```

## Configuration Modes

### Mode 1: Chart-Managed Gateway (Default)

The chart creates and manages its own Gateway resource:

```yaml
gateway:
  enabled: true
  gatewayClassName: istio
  hostname: "galaxy.example.com"
  create: true  # default
  
  # Optional TLS
  tls:
    enabled: true
    certificateRef: "galaxy-tls-cert"
```

### Mode 2: Existing Shared Gateway

Use a cluster-wide Gateway managed by platform teams:

```yaml
gateway:
  enabled: true
  existingGateway: "shared-gateway"
  existingGatewayNamespace: "istio-system"
  hostname: "galaxy.example.com"
```

### Mode 3: Default Gateway (Gateway API v1.4+)

Let Gateway API automatically attach HTTPRoutes to the default Gateway:

```yaml
gateway:
  enabled: true
  create: false  # No Gateway or existingGateway specified
  gatewayClassName: istio
  hostname: "galaxy.example.com"
```

## Architecture

```
User Traffic
     │
     ▼
┌─────────────────────┐
│ Gateway Controller  │  ← Istio/Cilium/Traefik/Kong/etc.
│ (External Routing)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ galaxy-nginx        │  ← Internal proxy (always present)
│ (Internal Routing)  │    • Static files
└──────────┬──────────┘    • x-accel-redirect
           │                • Connection buffering
           ▼
┌─────────────────────┐
│ Galaxy Handlers     │
│ • Web (Gunicorn)    │
│ • Job               │
│ • Workflow          │
│ • Celery            │
└─────────────────────┘
```

**Key Point**: The internal `galaxy-nginx` deployment is **never affected** by the choice of external routing (Ingress vs Gateway API). It provides critical functionality that Gateway implementations don't handle.

## Routing Resources

The chart creates three HTTPRoute resources when `gateway.enabled: true`:

1. **`httproute.yaml`** - Main Galaxy interface (`/galaxy`, `/training-material`)
2. **`httproute-tusd.yaml`** - Resumable uploads (`/galaxy/api/upload/resumable_upload`)
3. **`httproute-activity-canary.yaml`** - Autoscaling detection (`/galaxy/api/users`)

These replace the equivalent Ingress resources and provide the same functionality.

## Gateway Implementation Examples

### Istio

```yaml
gateway:
  enabled: true
  gatewayClassName: istio
  requestTimeout: "600s"
```

For production Istio deployments, apply the policies from `examples/gateway-policies/istio-policies.yaml`:

```bash
# Customize the examples for your deployment
cp examples/gateway-policies/istio-policies.yaml istio-galaxy-policies.yaml
# Edit file to match your release name, namespace, hostname
kubectl apply -f istio-galaxy-policies.yaml -n galaxy
```

The example includes VirtualService for timeouts/retries and EnvoyFilter for request size limits.

### Cilium

```yaml
gateway:
  enabled: true
  gatewayClassName: cilium
  hostname: "galaxy.example.com"
```

For advanced Cilium configuration, see `examples/gateway-policies/cilium-policies.yaml`. Cilium works with standard Gateway API and uses eBPF for high-performance routing.

### Traefik

```yaml
gateway:
  enabled: true
  gatewayClassName: traefik
```

For Traefik middleware configuration, see `examples/gateway-policies/traefik-policies.yaml`. Apply the middleware after customizing for your deployment.

### Kong

```yaml
gateway:
  enabled: true
  gatewayClassName: kong
```

For Kong plugin configuration, see `examples/gateway-policies/kong-policies.yaml`. The examples include timeout, request size, CORS, and rate limiting plugins.

### Nginx Gateway Fabric

```yaml
gateway:
  enabled: true
  gatewayClassName: nginx
```

For Nginx Gateway Fabric policies, see `examples/gateway-policies/nginx-policies.yaml`. The examples include ClientSettingsPolicy and BackendTLSPolicy configurations.

## Vendor-Specific Policy Examples

The chart maintains vendor neutrality by not including implementation-specific policies in the templates. Instead, comprehensive examples are provided in the `examples/gateway-policies/` directory:

| Implementation | Example File | Features |
|----------------|--------------|----------|
| Istio | `istio-policies.yaml` | VirtualService, EnvoyFilter |
| Kong | `kong-policies.yaml` | KongPlugins for timeouts, CORS, rate limiting |
| Cilium | `cilium-policies.yaml` | CiliumNetworkPolicy, annotations |
| Traefik | `traefik-policies.yaml` | Middlewares for common features |
| Nginx Gateway Fabric | `nginx-policies.yaml` | ClientSettingsPolicy, BackendTLSPolicy |

**Usage**:
1. Copy the example for your Gateway implementation
2. Customize values marked with `# CUSTOMIZE:`
3. Apply after installing Galaxy: `kubectl apply -f <policy-file> -n <namespace>`

See `examples/gateway-policies/README.md` for detailed instructions.

## Migration from Ingress

### Step 1: Backup Current Configuration

```bash
helm get values my-galaxy -n galaxy > galaxy-values-backup.yaml
kubectl get ingress -n galaxy -o yaml > ingress-backup.yaml
```

### Step 2: Install Gateway Controller

Follow the installation guide for your chosen Gateway implementation (see Prerequisites section).

### Step 3: Update Configuration

```bash
# Option A: In-place upgrade
helm upgrade my-galaxy galaxy/ -n galaxy \
  --set gateway.enabled=true \
  --set ingress.enabled=false \
  --set gateway.gatewayClassName=istio

# Option B: Blue-green deployment
helm install my-galaxy-v2 galaxy/ -n galaxy-v2 --create-namespace \
  --set gateway.enabled=true \
  --set ingress.enabled=false \
  --set gateway.gatewayClassName=istio
```

### Step 4: Verify Migration

```bash
# Check Gateway status
kubectl get gateway -n galaxy
kubectl describe gateway -n galaxy

# Check HTTPRoute status  
kubectl get httproute -n galaxy
kubectl describe httproute -n galaxy

# Test Galaxy access
curl -H "Host: galaxy.example.com" http://<gateway-ip>/galaxy/
```

### Rollback if Needed

```bash
helm upgrade my-galaxy galaxy/ -n galaxy \
  --set gateway.enabled=false \
  --set ingress.enabled=true
```

## Interactive Tools

**Requirements**: Galaxy 24.1+ for Gateway API support

Interactive Tools work by having Galaxy dynamically create HTTPRoute resources at job runtime. This requires:

1. **Wildcard DNS**: `*.its.<hostname>` resolving to your Gateway
2. **RBAC permissions**: Galaxy service account can create HTTPRoutes
3. **Gateway API support** in Galaxy job configuration (automatic when `gateway.enabled: true`)

The chart automatically configures Galaxy's job runner when Gateway API is enabled:

```yaml
# Automatically set in job_conf.yml when gateway.enabled: true
runners:
  k8s:
    k8s_interactivetools_use_gateway_api: true
    k8s_interactivetools_gateway_name: "{{ gateway name }}"
    k8s_interactivetools_gateway_namespace: "{{ gateway namespace }}"
```

### Verifying Interactive Tools

```bash
# Launch an interactive tool in Galaxy UI
# Check that HTTPRoute was created
kubectl get httproute -n galaxy -l "interactivetool=true"

# Check tool accessibility
curl https://it-abc123.its.galaxy.example.com/
```

## Production Considerations

### Timeouts

Different Gateway implementations handle timeouts differently. The chart sets `requestTimeout: "600s"` by default, but you may need additional vendor-specific policies:

- **Large file uploads**: Ensure backend timeout ≥ upload time
- **Long-running workflows**: Consider per-route timeout overrides  
- **Interactive tools**: May need extended idle timeouts

### Request Size Limits

Gateway implementations have varying default body size limits:

- **Istio**: Configure via EnvoyFilter
- **Kong**: Use request-size-limiting plugin
- **Nginx**: Set client_max_body_size equivalent
- **Traefik**: Configure via middleware

### TLS Termination

```yaml
gateway:
  tls:
    enabled: true
    certificateRef: "galaxy-tls-cert"  # Reference to TLS Secret
```

Ensure your certificate covers both the main hostname and Interactive Tools wildcard (`*.its.hostname`).

### Multi-Tenancy

For shared Gateway scenarios:

```yaml
# Platform team creates shared Gateway
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: shared-gateway
  namespace: istio-system
spec:
  gatewayClassName: istio
  listeners:
  - name: http
    port: 80
    protocol: HTTP
  - name: https  
    port: 443
    protocol: HTTPS
    tls:
      mode: Terminate
      certificateRefs:
      - name: wildcard-cert

---
# Each Galaxy instance references it
galaxy:
  enabled: true
  existingGateway: "shared-gateway"
  existingGatewayNamespace: "istio-system"
```

## Troubleshooting

### Gateway Not Ready

```bash
kubectl describe gateway -n galaxy
```

Common issues:
- **GatewayClass not found**: Install Gateway controller
- **Certificate not found**: Create TLS Secret
- **Invalid listeners**: Check hostname/port configuration

### HTTPRoute Not Working

```bash
kubectl describe httproute -n galaxy
```

Check:
- **parentRefs match Gateway**: Name and namespace correct
- **Backend service exists**: `kubectl get svc galaxy-nginx -n galaxy`
- **Gateway has matching listener**: Protocol, hostname, port align

### 502/504 Errors

Usually indicate backend issues, not Gateway problems:

```bash
# Check internal nginx
kubectl logs -n galaxy deployment/galaxy-nginx

# Check Galaxy handlers
kubectl get pods -n galaxy -l app.kubernetes.io/name=galaxy
kubectl logs -n galaxy deployment/galaxy-web-handler
```

### Timeouts Still Occurring

Verify vendor-specific timeout policies are applied:

```bash
# Istio
kubectl get virtualservice -n galaxy
kubectl describe virtualservice -n galaxy

# Kong  
kubectl get kongplugin -n galaxy

# Check HTTPRoute annotations
kubectl describe httproute -n galaxy
```

## Testing

### Template Validation

```bash
# Verify Gateway API resources created
helm template my-galaxy galaxy/ --set gateway.enabled=true | grep -E "kind: (Gateway|HTTPRoute)"

# Verify Ingress disabled
helm template my-galaxy galaxy/ --set gateway.enabled=true | grep "kind: Ingress"
# Should return nothing

# Test different modes
helm template my-galaxy galaxy/ \
  --set gateway.enabled=true \
  --set gateway.create=false  # Default Gateway mode

helm template my-galaxy galaxy/ \
  --set gateway.enabled=true \
  --set gateway.existingGateway=shared \
  --set gateway.existingGatewayNamespace=istio-system  # Shared Gateway mode
```

### Runtime Testing

```bash
# Check resource status
kubectl get gateway,httproute -n galaxy

# Test main Galaxy endpoint
curl -v -H "Host: galaxy.example.com" http://<gateway-ip>/galaxy/

# Test TUSD uploads (requires authentication)
curl -v -H "Host: galaxy.example.com" http://<gateway-ip>/galaxy/api/upload/resumable_upload

# Test activity canary (for autoscaling)
curl -v -H "Host: galaxy.example.com" http://<gateway-ip>/galaxy/api/users
```

## Supported Implementations

| Implementation | Status | Notes |
|----------------|--------|-------|
| **Istio** | ✅ Tested | Comprehensive features, production ready |
| **Cilium** | ✅ Tested | Good performance, eBPF-based |
| **Kong** | ✅ Compatible | Rich plugin ecosystem |
| **Traefik** | ✅ Compatible | Easy setup, good for dev/test |
| **Nginx Gateway Fabric** | ✅ Compatible | F5/Nginx official implementation |
| **Envoy Gateway** | ⚠️ Experimental | Newer project, less mature |

## Getting Help

- **Chart issues**: [galaxy-helm GitHub repository](https://github.com/galaxyproject/galaxy-helm/issues)
- **Gateway API**: [Official documentation](https://gateway-api.sigs.k8s.io/)
- **Galaxy community**: [Community chat](https://gitter.im/galaxyproject/Lobby)
- **Implementation-specific**:
  - [Istio Gateway API](https://istio.io/latest/docs/tasks/traffic-management/ingress/gateway-api/)
  - [Cilium Gateway API](https://docs.cilium.io/en/stable/network/servicemesh/gateway-api/)
  - [Kong Gateway API](https://docs.konghq.com/kubernetes-ingress-controller/latest/guides/using-gateway-api/)