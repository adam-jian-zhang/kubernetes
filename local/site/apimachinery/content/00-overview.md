---
title: "Overview"
weight: 0
---


## Introduction

`k8s.io/apimachinery` is a foundational library that provides the core machinery for working with Kubernetes API objects. It is a shared dependency for servers and clients to work with Kubernetes API infrastructure without direct type dependencies. This library is designed to support versioned APIs, type-safe serialization/deserialization, and conversion between different API versions.

## Purpose

The primary purpose of apimachinery is to provide:

1. **Scheme Management**: Type registry for converting group, version, and kind information to and from Go schemas
2. **Serialization/Deserialization**: Encoding and decoding API objects in multiple formats (JSON, YAML, Protobuf, CBOR)
3. **Version Conversion**: Converting objects between different API versions
4. **Metadata Handling**: Working with API object metadata (labels, annotations, resource versions)
5. **Selection**: Label and field selectors for filtering objects
6. **Watch Interface**: Observing changes to API objects
7. **Utility Functions**: Common utilities for validation, patching, and resource management

## High-Level Architecture

![Diagram](/diagrams/diagram-d09c6889.svg)

## Key Components

### 1. Runtime Package (`pkg/runtime`)

The runtime package is the heart of apimachinery, providing:

- **Scheme**: Central registry that maps Go types to GroupVersionKind (GVK)
- **Object Interface**: Base interface that all API objects must implement
- **Encoder/Decoder**: Interfaces for serializing and deserializing objects
- **Codec**: Combined encoder/decoder with version awareness
- **ObjectConvertor**: Converts objects between different versions
- **ObjectTyper**: Extracts type information from objects

![Diagram](/diagrams/diagram-207d6e3f.svg)

### 2. API Meta Package (`pkg/api/meta`)

Handles API object metadata and resource mapping:

- **MetadataAccessor**: Access object metadata (name, namespace, labels, annotations)
- **RESTMapper**: Maps between GroupVersionKind and GroupVersionResource
- **RESTMapping**: Contains information for RESTful resource access
- **Conditions**: Manages status conditions on objects

### 3. Conversion Package (`pkg/conversion`)

Provides automatic and manual conversion between different versions:

- **Converter**: Core conversion engine
- **Conversion Functions**: Auto-generated and manual conversion functions
- **Deep Copy**: Creates deep copies of objects

### 4. Labels Package (`pkg/labels`)

Implements label selectors for filtering objects:

- **Selector Interface**: Matches labels against requirements
- **Requirement**: Individual label requirement (key, operator, values)
- **Operators**: Equals, NotEquals, In, NotIn, Exists, DoesNotExist, GreaterThan, LessThan

### 5. Fields Package (`pkg/fields`)

Similar to labels but for field-based selection:

- **Selector Interface**: Matches fields against requirements
- **Field-based filtering**: Filter objects by field values

### 6. Watch Package (`pkg/watch`)

Provides interfaces for watching resource changes:

- **Interface**: Core watch interface
- **Event**: Represents a change (Added, Modified, Deleted, Bookmark, Error)
- **StreamWatcher**: Watches a stream for events
- **Mux**: Multiplexes multiple watch sources

### 7. Serialization (`pkg/runtime/serializer`)

Multiple serialization formats:

- **JSON**: Standard JSON serialization
- **YAML**: YAML serialization (built on JSON)
- **Protobuf**: Binary protocol buffer serialization
- **CBOR**: Concise Binary Object Representation
- **Versioning**: Handles version conversion during serialization

### 8. Resource Package (`pkg/api/resource`)

Handles resource quantities:

- **Quantity**: Fixed-point representation of numbers (CPU, memory, storage)
- **Suffixes**: Binary (Ki, Mi, Gi) and decimal (m, k, M, G) suffixes
- **Arithmetic**: Safe arithmetic operations on quantities

### 9. Validation Package (`pkg/api/validation`)

Validates API objects:

- **Generic Validation**: Common validation rules
- **ObjectMeta Validation**: Validates metadata fields
- **Field Path**: Tracks validation error locations

### 10. Utility Packages (`pkg/util/*`)

Various utility functions:

- **Sets**: Type-safe set implementations
- **Wait**: Polling and retry utilities
- **Diff**: Object comparison
- **Patch**: JSON Patch, JSON Merge Patch, Strategic Merge Patch
- **ManagedFields**: Field ownership tracking
- **IntStr**: Integer or string type
- **Version**: Version comparison utilities

## Data Flow

![Diagram](/diagrams/diagram-163e95b1.svg)

## Type System

Kubernetes uses a sophisticated type system based on GroupVersionKind (GVK):

![Diagram](/diagrams/diagram-ae1daa08.svg)

- **Group**: API group (e.g., `apps`, `batch`, `core`)
- **Version**: API version (e.g., `v1`, `v1beta1`)
- **Kind**: Type name (e.g., `Pod`, `Deployment`)
- **Resource**: RESTful resource name (e.g., `pods`, `deployments`)

## Version Conversion Strategy

![Diagram](/diagrams/diagram-4c0e612e.svg)

All external versions convert through a single internal version, avoiding the need for N² conversion functions.

## Key Design Principles

1. **Type Safety**: Strong typing with Go's type system
2. **Version Independence**: Internal representation separate from external versions
3. **Extensibility**: Plugin architecture for codecs and converters
4. **Performance**: Efficient serialization and caching mechanisms
5. **Backward Compatibility**: Support for multiple API versions simultaneously
6. **No Breaking Changes**: External APIs never break, only extend
7. **Centralized Serialization**: All encoding/decoding goes through the scheme

## Package Organization

```
pkg/
├── api/                    # API-related utilities
│   ├── apitesting/        # Testing utilities
│   ├── equality/          # Semantic equality
│   ├── errors/            # API errors
│   ├── meta/              # Metadata access
│   ├── resource/          # Resource quantities
│   ├── validate/          # Validation helpers
│   └── validation/        # Object validation
├── apis/                   # API type definitions
│   └── meta/              # Meta API types (v1, v1beta1)
├── conversion/            # Type conversion
├── fields/                # Field selectors
├── labels/                # Label selectors
├── runtime/               # Core runtime
│   ├── schema/            # GVK/GVR definitions
│   └── serializer/        # Serialization formats
├── selection/             # Selection operators
├── types/                 # Common types
├── util/                  # Utility packages
│   ├── cache/             # Caching utilities
│   ├── diff/              # Object diffing
│   ├── errors/            # Error utilities
│   ├── httpstream/        # HTTP streaming
│   ├── intstr/            # Int or String type
│   ├── json/              # JSON utilities
│   ├── managedfields/     # Server-side apply
│   ├── mergepatch/        # Merge patching
│   ├── net/               # Network utilities
│   ├── sets/              # Set data structures
│   ├── strategicpatch/    # Strategic merge patch
│   ├── validation/        # Validation utilities
│   ├── wait/              # Polling/retry
│   └── yaml/              # YAML utilities
├── version/               # Version information
└── watch/                 # Watch interface
```

## Usage Patterns

### Registering Types

```go
scheme := runtime.NewScheme()
scheme.AddKnownTypes(schema.GroupVersion{Group: "apps", Version: "v1"},
    &Deployment{},
    &DeploymentList{},
)
```

### Encoding/Decoding

```go
codec := serializer.NewCodecFactory(scheme)
encoder := codec.EncoderForVersion(jsonSerializer, gv)
encoder.Encode(object, writer)

decoder := codec.UniversalDeserializer()
obj, gvk, err := decoder.Decode(data, nil, nil)
```

### Label Selection

```go
selector := labels.SelectorFromSet(labels.Set{"app": "nginx"})
if selector.Matches(labels.Set{"app": "nginx", "env": "prod"}) {
    // matches
}
```

### Watching Resources

```go
watcher, err := client.Watch(ctx, options)
for event := range watcher.ResultChan() {
    switch event.Type {
    case watch.Added:
        // handle addition
    case watch.Modified:
        // handle modification
    case watch.Deleted:
        // handle deletion
    }
}
```

## Dependencies

Key external dependencies:

- `gopkg.in/inf.v0`: Arbitrary precision decimals for Quantity
- `gopkg.in/yaml.v3`: YAML parsing
- `google.golang.org/protobuf`: Protocol buffers
- `github.com/fxamacker/cbor/v2`: CBOR encoding
- `sigs.k8s.io/structured-merge-diff`: Server-side apply
- `sigs.k8s.io/json`: JSON parsing with case-sensitive field names
- `k8s.io/kube-openapi`: OpenAPI schema generation

## Related Projects

- `k8s.io/api`: Kubernetes API type definitions
- `k8s.io/client-go`: Kubernetes client library
- `k8s.io/apiserver`: Generic API server implementation
- `k8s.io/apiextensions-apiserver`: Custom Resource Definitions

## Summary

`k8s.io/apimachinery` provides the foundational machinery for Kubernetes APIs:

- **Type System**: GroupVersionKind-based type identification
- **Serialization**: Multiple format support with version conversion
- **Metadata**: Rich metadata handling and resource mapping
- **Selection**: Powerful label and field selectors
- **Watch**: Real-time change notifications
- **Utilities**: Comprehensive utility functions for API operations

This library enables Kubernetes to maintain backward compatibility while evolving its APIs, support multiple serialization formats, and provide a consistent programming model for API objects.

