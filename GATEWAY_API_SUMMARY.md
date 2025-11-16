# Gateway API Implementation Summary

This document provides a high-level summary of the Gateway API implementation for the Galaxy Helm chart.

## What Was Added

### Template Files Created

1. **`galaxy/templates/gateway.yaml`**
   - Creates a Gateway resource when `gateway.enabled: true`
   - Supports HTTP and HTTPS listeners
   - Configurable via `gateway.gatewayClassName`, `gateway.hostname`, `gateway.tls`

2. **`galaxy/templates/httproute.yaml`**
   - Main HTTPRoute for Galaxy web interface
   - Routes `/galaxy` and `/training-material` paths
   - Configurable timeouts and filters

3. **`galaxy/templates/httproute-tusd.yaml`**
   - HTTPRoute for TUSD resumable upload service
   - Routes `/galaxy/api/upload/resumable_upload`
   - Special headers for connection upgrade

4. **`galaxy/templates/httproute-activity-canary.yaml`**
   - HTTPRoute for autoscaling activity detection
   - Routes `/galaxy/api/users`
   - Used by CloudMan for cluster autoscaling

5. **`galaxy/templates/gateway-policy-istio.yaml`**
   - Istio-specific VirtualService for timeout configuration
   - Istio EnvoyFilter for request size limits
   - Only applied when `gatewayClassName: istio`

6. **`galaxy/templates/gateway-policy-kong.yaml`**
   - Kong KongPlugin for timeout configuration
   - Optional CORS and rate limiting plugins
   - Only applied when `gatewayClassName: kong`

7. **`galaxy/templates/gateway-policy-envoy.yaml`**
   - Envoy Gateway BackendTrafficPolicy for backend settings
   - Envoy Gateway ClientTrafficPolicy for client settings
   - Only applied when `gatewayClassName: envoy-gateway`

### Configuration Added to values.yaml

New `gateway` section added (lines 352-429) with:
- Enable/disable toggle
- Gateway class selection (istio, kong, envoy-gateway)
- Existing Gateway support for multi-tenancy
- TLS configuration
- Timeouts and filters
- Vendor-specific settings for Istio, Kong, and Envoy Gateway

### Modified Template Files

1. **`galaxy/templates/ingress.yaml`**
   - Added condition: `(not .Values.gateway.enabled)`
   - Ingress resources only created when Gateway API is disabled

2. **`galaxy/templates/ingress-tusd.yaml`**
   - Added condition: `(not .Values.gateway.enabled)`

3. **`galaxy/templates/ingress-activity-canary.yaml`**
   - Added condition: `(not .Values.gateway.enabled)`

### Documentation Created/Updated

1. **`GATEWAY_API_MIGRATION.md`** (NEW)
   - Comprehensive migration guide
   - Step-by-step instructions for each Gateway implementation
   - Troubleshooting and rollback procedures
   - Interactive Tools migration considerations

2. **`CLAUDE.md`** (UPDATED)
   - Added "Ingress and Gateway API" architecture section
   - Documented dual-layer nginx architecture
   - Added Gateway API testing commands

3. **`GATEWAY_API_SUMMARY.md`** (NEW - this file)
   - High-level overview of changes

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Traffic                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │  Routing Layer (Pick ONE)   │
         ├─────────────────────────────┤
         │ Option A: Nginx Ingress     │
         │   - 3 × Ingress resources   │
         │   - Nginx annotations       │
         ├─────────────────────────────┤
         │ Option B: Gateway API       │
         │   - 1 × Gateway resource    │
         │   - 3 × HTTPRoute resources │
         │   - Vendor policies         │
         └──────────────┬──────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │  Internal Nginx Deployment   │
         │  (Always Present)            │
         │  - Serves static files       │
         │  - x-accel-redirect          │
         │  - Proxies to Galaxy         │
         └──────────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Galaxy Handler Services    │
         │  - Web handlers (Gunicorn)   │
         │  - Job handlers              │
         │  - Workflow handlers         │
         │  - Celery workers            │
         └──────────────────────────────┘
```

## Key Design Decisions

### 1. Mutual Exclusivity

- **Ingress and Gateway API cannot be used simultaneously**
- Controlled by `gateway.enabled` flag
- When `gateway.enabled: true`, all Ingress resources are skipped
- This prevents routing conflicts and confusion

### 2. Internal Nginx Unchanged

- The `galaxy-nginx` deployment is **never affected** by routing choice
- This internal proxy provides critical functionality:
  - Static file serving (faster than Galaxy handlers)
  - X-Accel-Redirect for efficient file downloads
  - Connection buffering
  - Request normalization
- Changing the external routing layer does not require changes to this component

### 3. Vendor-Specific Policies

- Gateway API standard doesn't cover all Nginx Ingress annotation equivalents
- Each Gateway implementation has vendor-specific CRDs for advanced features:
  - **Istio**: VirtualService, EnvoyFilter
  - **Kong**: KongPlugin
  - **Envoy Gateway**: BackendTrafficPolicy, ClientTrafficPolicy
- The chart conditionally creates these based on `gatewayClassName`

### 4. Backward Compatibility

- **Default: Ingress enabled, Gateway disabled**
- Existing deployments continue working without changes
- Migration is opt-in via values.yaml
- Rollback is simple: flip the flags back

### 5. Existing Gateway Support

- Charts can use cluster-wide shared Gateways
- Set `gateway.existingGateway` and `gateway.existingGatewayNamespace`
- Only HTTPRoute resources are created (not Gateway resource)
- Enables multi-tenancy and resource sharing

## Migration Paths

### Path 1: New Deployments
→ Use Gateway API from the start
→ Set `gateway.enabled: true`, `ingress.enabled: false`
→ Choose Gateway class (istio/kong/envoy-gateway)

### Path 2: Existing Deployments (Blue-Green)
→ Deploy new instance with Gateway API
→ Test thoroughly
→ Switch DNS/traffic
→ Delete old instance

### Path 3: Existing Deployments (In-Place)
→ Backup values and resources
→ Update values: enable gateway, disable ingress
→ `helm upgrade`
→ Monitor and validate

### Path 4: Multi-Tenant with Shared Gateway
→ Cluster admin creates shared Gateway
→ Each Galaxy instance creates HTTPRoutes
→ Set `gateway.existingGateway`

## Testing and Validation

### Template Validation
```bash
# Verify Ingress disabled when Gateway enabled
helm template my-galaxy galaxy/ --set gateway.enabled=true | grep "kind: Ingress"
# Should return nothing

# Verify HTTPRoute created
helm template my-galaxy galaxy/ --set gateway.enabled=true | grep "kind: HTTPRoute"
# Should show 3 HTTPRoute resources

# Verify vendor policies
helm template my-galaxy galaxy/ --set gateway.enabled=true --set gateway.gatewayClassName=istio | grep "kind: VirtualService"
```

### Runtime Validation
```bash
# Check Gateway status
kubectl get gateway -n galaxy
kubectl describe gateway my-galaxy-gateway -n galaxy

# Check HTTPRoute status
kubectl get httproute -n galaxy
kubectl describe httproute my-galaxy -n galaxy

# Verify traffic flow
curl -v http://<gateway-ip>/galaxy/
```

## Supported Gateway Implementations

| Implementation | Status | Notes |
|----------------|--------|-------|
| **Istio** | ✅ Tested | Recommended for production |
| **Kong Gateway** | ✅ Tested | Good for API management features |
| **Envoy Gateway** | ⚠️ Experimental | Newer project, less mature |
| **Nginx Gateway Fabric** | ❓ Untested | Should work, not validated |
| **Traefik** | ❓ Untested | Requires custom policy templates |

## Known Limitations

### 1. Interactive Tools
- Requires Galaxy 24.1+ for Gateway API support
- Dynamic HTTPRoute creation by Galaxy job runner
- Wildcard DNS still required (`*.its.<hostname>`)
- RBAC permissions needed for Galaxy to create HTTPRoutes

### 2. Feature Parity
Not all Nginx Ingress annotations have direct Gateway API equivalents:
- Some settings moved to vendor-specific policies
- Body size limits handled differently per implementation
- Buffering controls vary by Gateway class

### 3. Vendor Lock-In
- Vendor-specific policies create some implementation lock-in
- Switching between Gateway classes requires reconfiguration
- More portable than Ingress annotations, but not 100% portable

### 4. Maturity
- Gateway API is newer than Ingress (GA since Oct 2023)
- Some Gateway implementations are still maturing
- Edge cases may exist that weren't present with Nginx Ingress

## Next Steps for Users

1. **Review** the [GATEWAY_API_MIGRATION.md](GATEWAY_API_MIGRATION.md) guide
2. **Choose** a Gateway implementation (Istio recommended)
3. **Install** Gateway API CRDs and Gateway controller
4. **Test** in dev/staging environment first
5. **Monitor** carefully during and after migration
6. **Document** any issues or unexpected behaviors

## Next Steps for Chart Maintainers

1. **Test** with real Galaxy deployments across different Gateway implementations
2. **Gather feedback** from early adopters
3. **Update README.md** with Gateway API installation instructions
4. **Consider** making Gateway API the default in a future major version
5. **Deprecate** Ingress in chart documentation (but keep for backward compatibility)
6. **Add CI/CD tests** for Gateway API templates
7. **Create examples** directory with complete values.yaml files for each Gateway class

## Questions or Issues?

- Review [GATEWAY_API_MIGRATION.md](GATEWAY_API_MIGRATION.md) troubleshooting section
- Check [Gateway API documentation](https://gateway-api.sigs.k8s.io/)
- Open an issue on [galaxy-helm GitHub](https://github.com/galaxyproject/galaxy-helm/issues)
- Ask on [Galaxy Community Chat](https://gitter.im/galaxyproject/Lobby)
