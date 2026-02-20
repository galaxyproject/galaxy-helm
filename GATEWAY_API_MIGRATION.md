# Gateway API Migration Guide

This guide explains how to migrate from Nginx Ingress Controller to Gateway API for the Galaxy Helm chart.

## Table of Contents

- [Overview](#overview)
- [Why Gateway API?](#why-gateway-api)
- [Prerequisites](#prerequisites)
- [Architecture Changes](#architecture-changes)
- [Migration Strategies](#migration-strategies)
- [Step-by-Step Migration](#step-by-step-migration)
- [Gateway Implementation Guides](#gateway-implementation-guides)
- [Interactive Tools Considerations](#interactive-tools-considerations)
- [Troubleshooting](#troubleshooting)
- [Rollback Procedure](#rollback-procedure)

## Overview

Gateway API is the successor to Kubernetes Ingress, providing more advanced routing capabilities and better separation of concerns. The Galaxy Helm chart now supports both traditional Ingress and Gateway API routing mechanisms.

**Important**: The two mechanisms are **mutually exclusive**. When `gateway.enabled: true`, all Ingress resources are disabled.

## Why Gateway API?

1. **Standardization**: Gateway API is becoming a Kubernetes standard, with broad vendor support
2. **Advanced Features**: Native support for traffic splitting, header manipulation, retry policies
3. **Role-Oriented**: Clear separation between infrastructure (Gateway) and application (HTTPRoute) concerns
4. **Future-Proof**: Nginx Ingress Controller is being deprecated in favor of Gateway API implementations
5. **Multi-Tenancy**: Better support for shared Gateways across multiple applications

## Prerequisites

Before migrating, ensure you have:

1. **Kubernetes 1.27+** with Gateway API CRDs installed:
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.0.0/standard-install.yaml
   ```

2. **Gateway Controller** installed in your cluster. Choose one:
   - **Istio** (recommended for production): [Installation Guide](https://istio.io/latest/docs/setup/install/)
   - **Kong Gateway**: [Installation Guide](https://docs.konghq.com/kubernetes-ingress-controller/latest/deployment/install/)
   - **Envoy Gateway**: [Installation Guide](https://gateway.envoyproxy.io/latest/install/)

3. **Verify Gateway CRDs are available**:
   ```bash
   kubectl api-resources | grep gateway.networking.k8s.io
   ```
   You should see: `gateways`, `httproutes`, `referencegrants`, etc.

4. **Backup your current configuration**:
   ```bash
   helm get values my-galaxy -n galaxy > galaxy-values-backup.yaml
   kubectl get ingress -n galaxy -o yaml > ingress-backup.yaml
   ```

## Architecture Changes

### What Changes

| Component | Before (Ingress) | After (Gateway API) |
|-----------|------------------|---------------------|
| **Routing Resources** | 3 × Ingress | 3 × HTTPRoute |
| **External Gateway** | Nginx Ingress Controller | Gateway implementation (Istio/Kong/Envoy) |
| **Internal Nginx** | galaxy-nginx deployment | galaxy-nginx deployment (unchanged) |
| **Configuration** | Nginx annotations | Gateway filters + vendor policies |
| **Interactive Tools** | Dynamically create Ingress | Dynamically create HTTPRoute (Galaxy 24.1+) |

### What Stays the Same

- Internal `galaxy-nginx` deployment (serves static files, handles x-accel-redirect)
- All Galaxy handler deployments (web, job, workflow, celery)
- PostgreSQL, RabbitMQ, and other dependencies
- Persistent volumes and storage configuration
- Service definitions

## Migration Strategies

### Strategy 1: Blue-Green Deployment (Recommended for Production)

Deploy a new Galaxy instance with Gateway API alongside the existing Ingress-based deployment, then switch traffic.

**Pros**: Zero downtime, easy rollback
**Cons**: Requires 2× resources temporarily

### Strategy 2: In-Place Upgrade (Suitable for Dev/Test)

Upgrade the existing deployment to use Gateway API.

**Pros**: Minimal resource usage
**Cons**: Brief downtime during switch

### Strategy 3: Shared Gateway (Multi-Tenant Environments)

Use an existing cluster-wide Gateway for multiple Galaxy instances.

**Pros**: Resource efficiency, centralized traffic management
**Cons**: Requires coordination with cluster administrators

## Step-by-Step Migration

### Phase 1: Preparation

1. **Install Gateway Controller** (example with Istio):
   ```bash
   # Install Istio
   curl -L https://istio.io/downloadIstio | sh -
   cd istio-*
   ./bin/istioctl install --set profile=default -y

   # Verify installation
   kubectl get pods -n istio-system
   ```

2. **Create a test Gateway** (optional, for validation):
   ```bash
   kubectl apply -f - <<EOF
   apiVersion: gateway.networking.k8s.io/v1
   kind: Gateway
   metadata:
     name: test-gateway
     namespace: galaxy
   spec:
     gatewayClassName: istio
     listeners:
       - name: http
         protocol: HTTP
         port: 80
   EOF
   ```

### Phase 2: Update values.yaml

Create a new values file for Gateway API (`galaxy-gateway-values.yaml`):

```yaml
# Enable Gateway API
gateway:
  enabled: true
  gatewayClassName: istio  # or kong, envoy-gateway
  hostname: "galaxy.example.com"  # Optional: specific hostname

  # Option A: Let the chart create a Gateway
  # (Leave existingGateway empty)

  # Option B: Use existing shared Gateway
  existingGateway: "shared-gateway"
  existingGatewayNamespace: "istio-system"

  # TLS configuration
  tls:
    enabled: true
    certificateRef: "galaxy-tls-cert"

  # Request timeout (equivalent to nginx proxy-read-timeout)
  requestTimeout: "600s"

  # Istio-specific settings (if using Istio)
  istio:
    timeout: "600s"
    maxRequestHeadersKb: 96
    streamIdleTimeout: "600s"

# Disable traditional Ingress
ingress:
  enabled: false

# Keep all other settings from your existing values
# (database, persistence, handlers, etc.)
```

### Phase 3: Test Configuration

1. **Dry-run the upgrade**:
   ```bash
   helm upgrade my-galaxy galaxy/ -n galaxy \
     -f galaxy-gateway-values.yaml \
     --dry-run --debug | less
   ```

2. **Verify no Ingress resources are created**:
   ```bash
   helm template my-galaxy galaxy/ -n galaxy \
     -f galaxy-gateway-values.yaml | grep "kind: Ingress"
   # Should return nothing
   ```

3. **Verify HTTPRoute resources are created**:
   ```bash
   helm template my-galaxy galaxy/ -n galaxy \
     -f galaxy-gateway-values.yaml | grep -A 30 "kind: HTTPRoute"
   # Should show 3 HTTPRoute resources
   ```

### Phase 4: Perform Migration

**For Blue-Green Deployment:**

1. **Deploy new Galaxy instance with Gateway API**:
   ```bash
   helm install my-galaxy-v2 galaxy/ -n galaxy-v2 --create-namespace \
     -f galaxy-gateway-values.yaml
   ```

2. **Test the new deployment**:
   ```bash
   # Get Gateway IP/hostname
   kubectl get gateway -n galaxy-v2

   # Test access (adjust hostname as needed)
   curl -H "Host: galaxy.example.com" http://<gateway-ip>/galaxy/
   ```

3. **Switch DNS or load balancer** to point to new Gateway

4. **Monitor for issues**, then delete old deployment:
   ```bash
   helm delete my-galaxy -n galaxy
   ```

**For In-Place Upgrade:**

1. **Perform the upgrade**:
   ```bash
   helm upgrade my-galaxy galaxy/ -n galaxy \
     -f galaxy-gateway-values.yaml
   ```

2. **Monitor rollout**:
   ```bash
   kubectl rollout status deployment/my-galaxy-nginx -n galaxy
   kubectl get httproute -n galaxy
   kubectl get gateway -n galaxy
   ```

3. **Verify Galaxy is accessible**:
   ```bash
   curl http://<gateway-hostname>/galaxy/
   ```

### Phase 5: Interactive Tools Migration

**Critical**: Interactive Tools require Galaxy 24.1+ to support Gateway API.

1. **Check Galaxy version**:
   ```bash
   kubectl exec -n galaxy deployment/my-galaxy-web-handler -- \
     galaxy --version
   ```

2. **If Galaxy < 24.1**, you have two options:
   - Upgrade Galaxy to 24.1+
   - Keep Interactive Tools disabled until upgrade

3. **Update job configuration** (already handled in values.yaml if using chart defaults):
   ```yaml
   configs:
     job_conf.yml:
       runners:
         k8s:
           # These settings are automatically configured when gateway.enabled: true
           k8s_interactivetools_use_gateway_api: true
           k8s_interactivetools_gateway_name: "{{ gateway name }}"
           k8s_interactivetools_gateway_namespace: "{{ gateway namespace }}"
   ```

## Gateway Implementation Guides

### Istio-Specific Configuration

```yaml
gateway:
  enabled: true
  gatewayClassName: istio
  istio:
    timeout: "600s"
    maxRequestHeadersKb: 96
    streamIdleTimeout: "600s"
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure,refused-stream
```

**Required Istio resources** (automatically created by chart):
- `VirtualService` for timeout configuration
- `EnvoyFilter` for request size limits

### Kong-Specific Configuration

```yaml
gateway:
  enabled: true
  gatewayClassName: kong
  kong:
    timeout: 600000  # milliseconds
    cors:
      enabled: true
      origins:
        - "https://galaxy.example.com"
      methods:
        - GET
        - POST
        - PUT
        - DELETE
      credentials: true
    rateLimit:
      enabled: true
      minute: 1000
      hour: 50000
```

**Install Kong plugins**:
```bash
kubectl apply -f galaxy/templates/gateway-policy-kong.yaml
```

### Envoy Gateway-Specific Configuration

```yaml
gateway:
  enabled: true
  gatewayClassName: envoy-gateway
  envoy:
    requestTimeout: "600s"
    requestReceivedTimeout: "300s"
    loadBalancer:
      type: "RoundRobin"
```

**Required Envoy Gateway resources** (automatically created):
- `BackendTrafficPolicy` for backend settings
- `ClientTrafficPolicy` for client settings

## Interactive Tools Considerations

Interactive Tools are the **most complex** part of the migration because:

1. **Dynamic resource creation**: Galaxy creates Ingress/HTTPRoute resources at runtime
2. **Wildcard DNS required**: `*.its.<hostname>` must resolve
3. **Gateway API support**: Requires Galaxy 24.1+ or manual patching

### Verification Steps

1. **Check if Interactive Tools use Gateway API**:
   ```bash
   kubectl get httproute -n galaxy -l "interactivetool=true"
   ```

2. **Test an Interactive Tool**:
   - Launch a Jupyter notebook or other interactive tool in Galaxy
   - Check that HTTPRoute is created
   - Verify the tool is accessible at `https://it-xxx.its.galaxy.example.com`

3. **If Interactive Tools don't work**:
   - Check Galaxy logs: `kubectl logs -n galaxy deployment/my-galaxy-job-handler`
   - Verify RBAC permissions for creating HTTPRoutes
   - Check wildcard DNS is configured

## Troubleshooting

### Gateway not ready

```bash
kubectl describe gateway my-galaxy-gateway -n galaxy
```

Look for conditions and events. Common issues:
- Gateway class not found: Install the Gateway controller
- Certificate not found: Create TLS secret
- Invalid listener configuration: Check hostname and port settings

### HTTPRoute not routing traffic

```bash
kubectl describe httproute my-galaxy -n galaxy
```

Check:
- `parentRefs` matches Gateway name/namespace
- Backend service exists: `kubectl get svc my-galaxy-nginx -n galaxy`
- Gateway has matching listener (protocol, hostname, port)

### 502 Bad Gateway errors

Usually indicates backend service issues, not Gateway API problems:

```bash
# Check nginx pods
kubectl get pods -n galaxy -l app.kubernetes.io/component=galaxy-nginx

# Check nginx logs
kubectl logs -n galaxy -l app.kubernetes.io/component=galaxy-nginx

# Check if Galaxy handlers are ready
kubectl get pods -n galaxy -l app.kubernetes.io/name=galaxy
```

### Timeouts still occurring

Check vendor-specific timeout policies are applied:

**Istio:**
```bash
kubectl get virtualservice my-galaxy-timeouts -n galaxy
kubectl describe virtualservice my-galaxy-timeouts -n galaxy
```

**Kong:**
```bash
kubectl get kongplugin my-galaxy-timeout -n galaxy
kubectl describe httproute my-galaxy -n galaxy
# Check for konghq.com/plugins annotation
```

**Envoy Gateway:**
```bash
kubectl get backendtrafficpolicy my-galaxy-backend-policy -n galaxy
kubectl describe backendtrafficpolicy my-galaxy-backend-policy -n galaxy
```

### Large file uploads failing

Gateway implementations may have different default limits than Nginx:

**Istio**: Check EnvoyFilter for `max_request_headers_kb`
**Kong**: Add KongPlugin for body size
**Envoy Gateway**: Check ClientTrafficPolicy settings

## Rollback Procedure

If you need to rollback to Ingress:

1. **Restore values**:
   ```bash
   helm upgrade my-galaxy galaxy/ -n galaxy \
     --set gateway.enabled=false \
     --set ingress.enabled=true \
     --set ingress.ingressClassName=nginx
   ```

2. **Verify Ingress resources are created**:
   ```bash
   kubectl get ingress -n galaxy
   ```

3. **Update DNS** to point back to Nginx Ingress Controller (if changed)

4. **Clean up Gateway resources** (optional):
   ```bash
   kubectl delete httproute --all -n galaxy
   kubectl delete gateway my-galaxy-gateway -n galaxy
   ```

## Post-Migration Checklist

- [ ] Gateway is in `Programmed` state
- [ ] All HTTPRoute resources are `Accepted`
- [ ] Galaxy web interface is accessible
- [ ] File uploads work (test with small and large files)
- [ ] TUSD resumable uploads work
- [ ] Job submission works
- [ ] Workflow execution works
- [ ] Interactive Tools work (if enabled)
- [ ] Activity canary endpoint responds (if enabled)
- [ ] TLS certificate is valid (if using HTTPS)
- [ ] Monitoring/metrics still work
- [ ] Documentation updated with new access URLs

## Additional Resources

- [Gateway API Documentation](https://gateway-api.sigs.k8s.io/)
- [Istio Gateway API Guide](https://istio.io/latest/docs/tasks/traffic-management/ingress/gateway-api/)
- [Kong Gateway API Guide](https://docs.konghq.com/kubernetes-ingress-controller/latest/guides/using-gateway-api/)
- [Envoy Gateway Documentation](https://gateway.envoyproxy.io/)
- [Galaxy Interactive Tools Documentation](https://docs.galaxyproject.org/en/master/admin/special_topics/interactivetools.html)

## Getting Help

If you encounter issues during migration:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review Gateway/HTTPRoute status: `kubectl describe`
3. Check pod logs: `kubectl logs -n galaxy <pod-name>`
4. Open an issue on the [galaxy-helm GitHub repository](https://github.com/galaxyproject/galaxy-helm/issues)
5. Ask on the [Galaxy Community Chat](https://gitter.im/galaxyproject/Lobby)
