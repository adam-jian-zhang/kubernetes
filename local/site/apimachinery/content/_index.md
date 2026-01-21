---
title: "k8s.io/apimachinery Documentation"
weight: 0
---


## Overview

This documentation covers the `k8s.io/apimachinery` library, which provides the foundational machinery for working with Kubernetes API objects. It is a shared dependency for servers and clients to work with Kubernetes API infrastructure without direct type dependencies.

## What is apimachinery?

`k8s.io/apimachinery` is the core library that enables:

- **Type-safe API objects**: Strong typing with Go's type system
- **Version management**: Support for multiple API versions simultaneously
- **Serialization**: Multiple format support (JSON, YAML, Protobuf, CBOR)
- **Conversion**: Automatic conversion between API versions
- **Metadata handling**: Rich metadata access and manipulation
- **Selection**: Powerful label and field selectors
- **Watch interface**: Real-time change notifications
- **Utilities**: Comprehensive utility functions

## Documentation Structure

### Core Packages

1. **[Overview](00-overview/)** - High-level architecture and design principles
   - Purpose and goals
   - Key components
   - Data flow
   - Type system
   - Design principles

2. **[Runtime Package](01-runtime-package/)** - Core runtime machinery
   - Scheme (type registry)
   - Object interface
   - Encoder/Decoder interfaces
   - Codec system
   - Conversion system
   - Defaulting

3. **[API Meta Package](02-api-meta-package/)** - Metadata and resource mapping
   - Metadata accessors
   - RESTMapper
   - RESTMapping
   - Conditions management
   - Type conversions

4. **[Labels and Fields](03-labels-and-fields-packages/)** - Selection and filtering
   - Label selectors
   - Field selectors
   - Operators
   - Parsing
   - Matching

5. **[Watch Package](04-watch-package/)** - Real-time change notifications
   - Watch interface
   - Event types
   - StreamWatcher
   - Broadcaster
   - Mux
   - Filter

6. **[Serialization](05-serialization/)** - Multiple format support
   - CodecFactory
   - JSON serializer
   - YAML serializer
   - Protobuf serializer
   - CBOR serializer
   - Versioning codec
   - Streaming

7. **[Utility Packages](06-utility-packages/)** - Common utilities
   - wait (polling and retry)
   - sets (set data structures)
   - intstr (int or string type)
   - errors (error aggregation)
   - validation (field validation)
   - strategicpatch (Kubernetes patching)
   - mergepatch (JSON merge patch)
   - managedfields (server-side apply)
   - net (network utilities)
   - yaml (YAML utilities)
   - diff (object comparison)
   - version (version comparison)

8. **[Conversion and Resources](07-conversion-and-resources/)** - Version conversion and quantities
   - Conversion system
   - Hub-and-spoke pattern
   - Auto-generated conversions
   - Manual overrides
   - Resource quantities
   - Quantity formats
   - Arithmetic operations

## Quick Start

### Basic Usage

```go
import (
    "k8s.io/apimachinery/pkg/runtime"
    "k8s.io/apimachinery/pkg/runtime/schema"
    "k8s.io/apimachinery/pkg/runtime/serializer"
)

// Create a scheme
scheme := runtime.NewScheme()

// Register types
scheme.AddKnownTypes(
    schema.GroupVersion{Group: "apps", Version: "v1"},
    &Deployment{},
    &DeploymentList{},
)

// Create codec factory
codecFactory := serializer.NewCodecFactory(scheme)

// Get universal deserializer
decoder := codecFactory.UniversalDeserializer()

// Decode object
obj, gvk, err := decoder.Decode(data, nil, nil)
```

### Common Patterns

#### 1. Encoding/Decoding

```go
// Encode to JSON
encoder := codecFactory.EncoderForVersion(
    jsonSerializer,
    schema.GroupVersion{Group: "apps", Version: "v1"},
)
var buf bytes.Buffer
err := encoder.Encode(deployment, &buf)

// Decode from any format
decoder := codecFactory.UniversalDeserializer()
obj, gvk, err := decoder.Decode(data, nil, nil)
```

#### 2. Label Selection

```go
// Create selector
selector, err := labels.Parse("app=nginx,env in (prod,staging)")

// Match labels
if selector.Matches(labels.Set(pod.Labels)) {
    // Pod matches selector
}
```

#### 3. Watching Resources

```go
watcher, err := client.Watch(ctx, options)
defer watcher.Stop()

for event := range watcher.ResultChan() {
    switch event.Type {
    case watch.Added:
        // Handle addition
    case watch.Modified:
        // Handle modification
    case watch.Deleted:
        // Handle deletion
    }
}
```

#### 4. Polling with Retry

```go
err := wait.Poll(time.Second, 5*time.Minute, func() (bool, error) {
    pod, err := client.Get(ctx, name, metav1.GetOptions{})
    if err != nil {
        return false, err
    }
    return pod.Status.Phase == v1.PodRunning, nil
})
```

## Key Concepts

### GroupVersionKind (GVK)

Uniquely identifies an API type:

```go
type GroupVersionKind struct {
    Group   string  // e.g., "apps"
    Version string  // e.g., "v1"
    Kind    string  // e.g., "Deployment"
}
```

### GroupVersionResource (GVR)

Identifies a REST resource:

```go
type GroupVersionResource struct {
    Group    string  // e.g., "apps"
    Version  string  // e.g., "v1"
    Resource string  // e.g., "deployments"
}
```

### Scheme

Central type registry that maps Go types to GVK:

```go
type Scheme struct {
    gvkToType map[GroupVersionKind]reflect.Type
    typeToGVK map[reflect.Type][]GroupVersionKind
    converter *conversion.Converter
    // ... more fields
}
```

### Object Interface

Base interface for all API objects:

```go
type Object interface {
    GetObjectKind() schema.ObjectKind
    DeepCopyObject() Object
}
```

## Architecture Diagrams

### Overall Architecture

![Diagram](/diagrams/diagram-4a9f4eba.svg)

### Data Flow

![Diagram](/diagrams/diagram-78a0b1c9.svg)

## Package Dependencies

### External Dependencies

- `gopkg.in/inf.v0` - Arbitrary precision decimals
- `gopkg.in/yaml.v3` - YAML parsing
- `google.golang.org/protobuf` - Protocol buffers
- `github.com/fxamacker/cbor/v2` - CBOR encoding
- `sigs.k8s.io/structured-merge-diff` - Server-side apply
- `sigs.k8s.io/json` - JSON parsing
- `k8s.io/kube-openapi` - OpenAPI schema

### Related Kubernetes Projects

- `k8s.io/api` - Kubernetes API type definitions
- `k8s.io/client-go` - Kubernetes client library
- `k8s.io/apiserver` - Generic API server
- `k8s.io/apiextensions-apiserver` - Custom Resource Definitions

## Design Principles

1. **Type Safety**: Strong typing with Go's type system
2. **Version Independence**: Internal representation separate from external versions
3. **Extensibility**: Plugin architecture for codecs and converters
4. **Performance**: Efficient serialization and caching mechanisms
5. **Backward Compatibility**: Support for multiple API versions simultaneously
6. **No Breaking Changes**: External APIs never break, only extend
7. **Centralized Serialization**: All encoding/decoding goes through the scheme

## Common Use Cases

### 1. Building API Servers

```go
// Register types
scheme.AddKnownTypes(gv, types...)

// Create codec factory
codecFactory := serializer.NewCodecFactory(scheme)

// Handle HTTP requests
codec := codecFactory.CodecForVersions(encoder, decoder, encodeGV, decodeGV)
```

### 2. Building Clients

```go
// Decode server responses
decoder := codecFactory.UniversalDeserializer()
obj, gvk, err := decoder.Decode(responseBody, nil, nil)

// Encode client requests
encoder := codecFactory.EncoderForVersion(serializer, gv)
encoder.Encode(obj, requestBody)
```

### 3. Custom Controllers

```go
// Watch resources
watcher, err := client.Watch(ctx, options)

// Filter by labels
selector := labels.SelectorFromSet(labels.Set{"app": "myapp"})

// Poll for conditions
wait.PollUntil(interval, condition, stopCh)
```

### 4. Custom Resource Definitions

```go
// Register custom types
scheme.AddKnownTypes(gv, &MyResource{}, &MyResourceList{})

// Add conversion functions
scheme.AddConversionFunc(...)

// Add defaulting functions
scheme.AddTypeDefaultingFunc(...)
```

## Testing

### Test Utilities

- `runtime/testing` - Runtime testing utilities
- `api/apitesting` - API testing utilities
- `watch.NewFake()` - Fake watcher for testing
- `labels.Everything()` - Match-all selector

### Example Test

```go
func TestEncoding(t *testing.T) {
    scheme := runtime.NewScheme()
    scheme.AddKnownTypes(gv, &MyType{})
    
    codecFactory := serializer.NewCodecFactory(scheme)
    codec := codecFactory.LegacyCodec(gv)
    
    original := &MyType{Name: "test"}
    
    // Encode
    data, err := runtime.Encode(codec, original)
    require.NoError(t, err)
    
    // Decode
    decoded, err := runtime.Decode(codec, data)
    require.NoError(t, err)
    
    // Compare
    assert.Equal(t, original, decoded)
}
```

## Performance Tips

1. **Cache Selectors**: Parse selectors once, reuse many times
2. **Use Streaming**: For large collections, use streaming serialization
3. **Choose Right Format**: Protobuf for performance, JSON for debugging
4. **Reuse Codecs**: Create codec factory once, reuse encoders/decoders
5. **Batch Operations**: Use wait.Group for parallel operations
6. **Index by Labels**: Build indices for efficient label-based lookups

## Troubleshooting

### Common Issues

1. **Type Not Registered**: Ensure types are registered with scheme
2. **Version Conversion Fails**: Check conversion functions are registered
3. **Selector Parse Error**: Validate selector syntax
4. **Watch Disconnects**: Implement reconnection with resource version
5. **Quantity Parse Error**: Check format (e.g., "1Gi" not "1GB")

### Debug Tips

- Enable verbose logging with `klog`
- Use pretty printing for JSON debugging
- Check GVK with `scheme.ObjectKinds(obj)`
- Validate with strict mode serializers
- Test round-trip conversions

## Contributing

This is a staged repository. Contributions should be made to the main Kubernetes repository:
- https://github.com/kubernetes/kubernetes
- Path: `staging/src/k8s.io/apimachinery`

## License

Apache License 2.0

## Additional Resources

- [Kubernetes API Conventions](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md)
- [API Changes](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api_changes.md)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

## Summary

`k8s.io/apimachinery` provides the foundational machinery for Kubernetes APIs:

- **Type System**: GVK-based type identification with Scheme registry
- **Serialization**: Multiple format support with content negotiation
- **Conversion**: Hub-and-spoke version conversion
- **Metadata**: Rich metadata handling and resource mapping
- **Selection**: Powerful label and field selectors
- **Watch**: Real-time change notifications
- **Utilities**: Comprehensive utility functions

This library is essential for anyone building on Kubernetes, whether creating custom controllers, operators, API servers, or client applications.

