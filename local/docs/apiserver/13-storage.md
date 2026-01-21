# pkg/storage - Storage Layer

## Overview

The `pkg/storage` package provides the storage interface and implementations for persisting Kubernetes objects. It abstracts the underlying storage backend (typically etcd) and provides features like watch caching, encryption, and efficient list/watch operations.

## Purpose

The storage layer:
- **Storage Abstraction**: Unified interface for different storage backends
- **Watch Cache**: In-memory cache for efficient watch operations
- **Encryption**: Transparent encryption at rest
- **Optimistic Concurrency**: ResourceVersion-based conflict detection
- **Efficient Operations**: Optimized list, watch, and pagination

## Architecture

```mermaid
graph TB
    subgraph "Storage Stack"
        A[REST Storage] --> B[storage.Interface]
        B --> C[Cacher]
        C --> D[Transformer]
        D --> E[etcd3]
        E --> F[etcd Cluster]
    end
    
    subgraph "Watch Cache"
        G[Watch Requests] --> C
        C --> H[In-Memory Cache]
        H --> I[Event Buffer]
    end
    
    style B fill:#e6f3ff
    style C fill:#fff4e6
    style E fill:#ffe6e6
```

## Core Interface

```go
type Interface interface {
    Versioner() Versioner
    Create(ctx context.Context, key string, obj, out runtime.Object, ttl uint64) error
    Delete(ctx context.Context, key string, out runtime.Object, preconditions *Preconditions, validateDeletion ValidateObjectFunc, cachedExistingObject runtime.Object) error
    Watch(ctx context.Context, key string, opts ListOptions) (watch.Interface, error)
    Get(ctx context.Context, key string, opts GetOptions, objPtr runtime.Object) error
    GetList(ctx context.Context, key string, opts ListOptions, listObj runtime.Object) error
    GuaranteedUpdate(ctx context.Context, key string, destination runtime.Object, ignoreNotFound bool, preconditions *Preconditions, tryUpdate UpdateFunc, cachedExistingObject runtime.Object) error
    Count(key string) (int64, error)
}
```

## Key Components

### 1. Cacher

Located in `cacher/`:

```mermaid
graph TB
    A[Watch Request] --> B{Cache Ready?}
    B -->|Yes| C[Serve from Cache]
    B -->|No| D[Wait for Ready]
    D --> C
    C --> E[Event Stream]
    
    F[etcd Watch] --> G[Update Cache]
    G --> H[Notify Watchers]
    
    style B fill:#e6f3ff
    style G fill:#fff4e6
```

**Features**:
- In-memory object cache
- Event history buffer
- Bookmark support
- Consistent reads
- Fall-through to etcd

### 2. etcd3 Storage

Located in `etcd3/`:

Direct etcd v3 client implementation:

```go
type store struct {
    client *clientv3.Client
    codec runtime.Codec
    versioner Versioner
    transformer value.Transformer
    pathPrefix string
    watcher *watcher
    pagingEnabled bool
    leaseManager *leaseManager
}
```

### 3. Value Transformer

Located in `value/`:

Transforms values before storage (e.g., encryption):

```mermaid
graph LR
    A[Plain Object] --> B[Transformer]
    B --> C[Encrypted Object]
    C --> D[etcd]
    
    D --> E[Transformer]
    E --> F[Plain Object]
    
    style B fill:#e6f3ff
    style E fill:#fff4e6
```

**Transformers**:
- **Identity**: No transformation
- **Prefix**: Add prefix
- **AES-CBC**: AES encryption
- **AES-GCM**: AES-GCM encryption
- **KMS**: External KMS encryption

## Operations

### Create

```mermaid
sequenceDiagram
    participant Client
    participant Storage
    participant Transformer
    participant etcd
    
    Client->>Storage: Create(key, obj)
    Storage->>Transformer: Transform(obj)
    Transformer-->>Storage: Encrypted obj
    Storage->>etcd: Put(key, data)
    etcd-->>Storage: Success
    Storage-->>Client: Created obj
```

### Get

```mermaid
sequenceDiagram
    participant Client
    participant Storage
    participant Cache
    participant etcd
    
    Client->>Storage: Get(key)
    Storage->>Cache: Lookup
    alt Cache Hit
        Cache-->>Storage: Cached obj
    else Cache Miss
        Storage->>etcd: Get(key)
        etcd-->>Storage: Data
        Storage->>Cache: Update
    end
    Storage-->>Client: Object
```

### List

```mermaid
sequenceDiagram
    participant Client
    participant Storage
    participant Cache
    participant etcd
    
    Client->>Storage: List(prefix, options)
    alt From Cache
        Storage->>Cache: List
        Cache-->>Storage: Objects
    else From etcd
        Storage->>etcd: Range(prefix)
        etcd-->>Storage: Objects
    end
    Storage->>Storage: Filter & Paginate
    Storage-->>Client: ObjectList
```

### Watch

```mermaid
sequenceDiagram
    participant Client
    participant Storage
    participant Cache
    participant etcd
    
    Client->>Storage: Watch(key, resourceVersion)
    Storage->>Cache: Watch
    Cache->>Cache: Check RV
    alt RV in buffer
        Cache-->>Client: Events from buffer
    else RV too old
        Storage->>etcd: Watch from RV
        etcd-->>Client: Events
    end
    
    loop Ongoing
        etcd->>Cache: New event
        Cache->>Client: Forward event
    end
```

### GuaranteedUpdate

```mermaid
sequenceDiagram
    participant Client
    participant Storage
    participant UpdateFunc
    participant etcd
    
    Client->>Storage: GuaranteedUpdate(key, updateFunc)
    loop Until Success
        Storage->>etcd: Get(key)
        etcd-->>Storage: Current obj + RV
        Storage->>UpdateFunc: Call(current)
        UpdateFunc-->>Storage: Updated obj
        Storage->>etcd: Put(key, obj, RV)
        alt Success
            etcd-->>Storage: Success
        else Conflict
            etcd-->>Storage: Conflict (retry)
        end
    end
    Storage-->>Client: Final obj
```

## Watch Cache

### Initialization

```mermaid
sequenceDiagram
    participant Cacher
    participant etcd
    
    Cacher->>etcd: List (get initial state)
    etcd-->>Cacher: Objects + RV
    Cacher->>Cacher: Populate cache
    Cacher->>etcd: Watch from RV
    etcd-->>Cacher: Event stream
    Cacher->>Cacher: Mark ready
```

### Event Processing

```mermaid
graph TB
    A[etcd Event] --> B[Update Cache]
    B --> C[Add to Buffer]
    C --> D[Notify Watchers]
    D --> E[Send to Clients]
    
    F[Bookmark] --> G[Update RV]
    G --> C
    
    style B fill:#e6f3ff
    style D fill:#fff4e6
```

## Pagination

```go
type ListOptions struct {
    Predicate SelectionPredicate
    Recursive bool
    ResourceVersion string
    ResourceVersionMatch ResourceVersionMatch
    Limit int64
    Continue string
}
```

**Pagination Flow**:
1. Client requests with Limit
2. Server returns up to Limit items
3. Server includes Continue token if more items exist
4. Client uses Continue token for next page

## Consistency Guarantees

### Resource Version

```mermaid
graph LR
    A[ResourceVersion] --> B{Type}
    B -->|Empty| C[Any Version]
    B -->|0| D[Most Recent]
    B -->|Specific| E[Exact Version]
    
    C --> F[May be stale]
    D --> G[Consistent read]
    E --> H[Consistent read]
    
    style B fill:#e6f3ff
```

### ResourceVersionMatch

- **NotOlderThan**: Return data at least as fresh as provided RV
- **Exact**: Return data at exactly the provided RV

## Package Structure

```
pkg/storage/
├── interfaces.go           # Core storage interface
├── selection_predicate.go  # Filtering predicates
├── cacher/                 # Watch cache implementation
│   ├── cacher.go          # Main cacher
│   ├── watch_cache.go     # Watch cache
│   └── cache_watcher.go   # Cache watcher
├── etcd3/                  # etcd v3 implementation
│   ├── store.go           # Main store
│   ├── watcher.go         # Watch implementation
│   ├── compact.go         # Compaction
│   └── metrics/           # Storage metrics
├── value/                  # Value transformation
│   ├── transformer.go     # Transformer interface
│   ├── encrypt/           # Encryption transformers
│   └── metrics/           # Transformation metrics
├── storagebackend/         # Storage backend configuration
│   └── factory.go
└── testing/                # Testing utilities
    └── utils.go
```

## Encryption at Rest

```mermaid
graph TB
    A[Object] --> B[Serialize]
    B --> C[Encrypt]
    C --> D[Store in etcd]
    
    D --> E[Read from etcd]
    E --> F[Decrypt]
    F --> G[Deserialize]
    G --> H[Object]
    
    style C fill:#ffe6e6
    style F fill:#ffe6e6
```

**Encryption Providers**:
- **identity**: No encryption
- **aescbc**: AES-CBC encryption
- **aesgcm**: AES-GCM encryption
- **secretbox**: NaCl Secretbox
- **kms**: External KMS (v1 and v2)

## Best Practices

### 1. Use Watch Cache

Enable watch cache for better performance:
```go
config := storagebackend.Config{
    Type: "etcd3",
    CacherConfig: &storage.CacherConfig{
        Size: 100,
        Clock: clock.RealClock{},
    },
}
```

### 2. Set Appropriate TTL

Use TTL for temporary objects:
```go
err := storage.Create(ctx, key, obj, out, 3600) // 1 hour TTL
```

### 3. Use Pagination

Paginate large lists:
```go
opts := storage.ListOptions{
    Predicate: predicate,
    Limit: 500,
}
```

### 4. Handle Conflicts

Retry on conflicts in GuaranteedUpdate:
```go
err := storage.GuaranteedUpdate(ctx, key, out, true, nil,
    func(input runtime.Object, res storage.ResponseMeta) (runtime.Object, *uint64, error) {
        // Update logic
        return updated, nil, nil
    }, nil)
```

## Related Packages

- **pkg/registry**: Uses storage interface
- **pkg/server**: Configures storage
- **k8s.io/apimachinery/pkg/watch**: Watch interface

## References

- [etcd Documentation](https://etcd.io/docs/)
- [Encryption at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
