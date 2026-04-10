# Gateway Policy Examples

This directory contains example vendor-specific policies for Galaxy Gateway API deployments. The Galaxy Helm chart creates standard Gateway API resources (Gateway, HTTPRoute) but doesn't include vendor-specific policies to maintain vendor neutrality.

These examples show how to configure common features like timeouts, request size limits, and other advanced routing features for different Gateway implementations.

## Available Examples

| Implementation | File | Features |
|----------------|------|----------|
| **Istio** | `istio-policies.yaml` | VirtualService (timeouts, retries), EnvoyFilter (request limits) |
| **Kong** | `kong-policies.yaml` | KongPlugins (timeout, request size, CORS, rate limiting) |
| **Cilium** | `cilium-policies.yaml` | CiliumNetworkPolicy, Gateway with annotations |
| **Traefik** | `traefik-policies.yaml` | Middlewares (timeout, request size, CORS, rate limiting) |
| **Nginx Gateway Fabric** | `nginx-policies.yaml` | ClientSettingsPolicy, BackendTLSPolicy |

## Usage

1. **Install Galaxy with Gateway API** first:
   ```bash
   helm install my-galaxy galaxy/ -n galaxy \
     --set gateway.enabled=true \
     --set gateway.gatewayClassName=istio \  # or kong, cilium, etc.
     --set ingress.enabled=false
   ```

2. **Customize the example policies**:
   - Edit the policy file for your Gateway implementation
   - Update values marked with `# CUSTOMIZE:`
     - Release name (e.g., `my-galaxy`)
     - Namespace (e.g., `galaxy`)
     - Hostname (e.g., `galaxy.example.com`)
     - Gateway name (if using existing Gateway)
     - Timeout values (adjust for your upload sizes)

3. **Apply the policies**:
   ```bash
   kubectl apply -f examples/gateway-policies/istio-policies.yaml -n galaxy
   ```

## Policy Categories

### Timeout Configuration

All Gateway implementations need custom timeout settings for Galaxy:

- **Request timeout**: 600s+ for large file uploads
- **Stream idle timeout**: 600s+ for long-running operations
- **Connection timeout**: Standard values (60s) are usually sufficient

**Why needed**: Galaxy can handle large genomic datasets requiring extended upload/processing times.

### Request Size Limits

Galaxy may receive large requests (file uploads, API calls with large payloads):

- **Request body size**: 50MB+ (adjust based on your upload requirements)
- **Request headers**: 96KB+ (Galaxy can send large headers)

**Why needed**: Default Gateway limits (1-10MB) are too small for typical Galaxy workflows.

### Optional Features

Some examples include additional policies:

- **CORS**: For browser-based Galaxy access
- **Rate limiting**: To prevent abuse
- **Retry policies**: For resilient operation
- **TLS configuration**: For secure backend communication

## Implementation-Specific Notes

### Istio
- Uses VirtualService for routing policies
- Uses EnvoyFilter for low-level Envoy configuration
- Most comprehensive feature set
- **Production ready**

### Kong
- Uses KongPlugin resources applied via HTTPRoute annotations
- Rich plugin ecosystem for advanced features
- Good for API management use cases
- **Production ready**

### Cilium
- Uses standard Gateway API with some annotations
- eBPF-based for high performance
- Limited vendor-specific features (relies on service mesh for advanced features)
- **Production ready**

### Traefik
- Uses Middleware resources applied via annotations or filters
- Good for development and small deployments
- Easy configuration and setup
- **Suitable for dev/test and small production**

### Nginx Gateway Fabric
- Uses policy resources that attach to Gateway/HTTPRoute
- Official F5/Nginx implementation
- Similar feature set to Nginx Ingress Controller
- **Suitable for production**

## Customization Guidelines

### Timeouts
- **Small files (< 1GB)**: 300-600s should be sufficient
- **Large files (> 10GB)**: Consider 1800s+ or disable timeouts
- **Interactive tools**: May need extended idle timeouts

### Request Size Limits
- **Basic Galaxy**: 50MB covers most use cases
- **Large dataset uploads**: 1GB+ may be needed
- **Reference data**: Usually handled via separate upload mechanisms

### Hostname Configuration
- **Main Galaxy**: `galaxy.example.com`
- **Interactive Tools**: Ensure wildcard DNS `*.its.galaxy.example.com` resolves
- **Development**: Can use `*` for any hostname

## Testing Your Configuration

After applying policies, test common Galaxy operations:

```bash
# Test basic Galaxy access
curl -v https://galaxy.example.com/galaxy/

# Test TUSD resumable uploads (requires authentication)
curl -v https://galaxy.example.com/galaxy/api/upload/resumable_upload

# Test with large request headers
curl -v -H "Large-Header: $(python3 -c 'print("x" * 50000)')" \
  https://galaxy.example.com/galaxy/api/users

# Monitor Gateway/HTTPRoute status
kubectl get gateway,httproute -n galaxy
kubectl describe httproute my-galaxy -n galaxy
```

## Troubleshooting

### Policy Not Applied
1. Check policy resource exists: `kubectl get <policy-type> -n galaxy`
2. Verify correct labels/selectors match your Gateway/HTTPRoute
3. Check Gateway controller logs for errors

### Timeouts Still Occurring
1. Verify policy targets correct Gateway/HTTPRoute names
2. Check if multiple policies conflict
3. Look for default timeout settings in Gateway controller configuration

### Request Size Limits Not Working
1. Confirm policy syntax matches your Gateway implementation version
2. Check both ingress and backend size limits are configured
3. Test with known request sizes to isolate the issue

## Contributing Examples

If you create policies for other Gateway implementations or discover better configurations:

1. Follow the existing file naming pattern: `<implementation>-policies.yaml`
2. Include comprehensive comments and customization markers
3. Test with a real Galaxy deployment
4. Submit a PR to the galaxy-helm repository

## References

- [Gateway API Documentation](https://gateway-api.sigs.k8s.io/)
- [Istio Gateway API](https://istio.io/latest/docs/tasks/traffic-management/ingress/gateway-api/)
- [Kong Gateway API](https://docs.konghq.com/kubernetes-ingress-controller/latest/guides/using-gateway-api/)
- [Cilium Gateway API](https://docs.cilium.io/en/stable/network/servicemesh/gateway-api/)
- [Traefik Gateway API](https://doc.traefik.io/traefik/routing/providers/kubernetes-gateway/)
- [Nginx Gateway Fabric](https://docs.nginx.com/nginx-gateway-fabric/)