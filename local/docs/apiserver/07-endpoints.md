# pkg/endpoints - REST Endpoint Handling

## Overview

The `pkg/endpoints` package implements the REST endpoint handling for Kubernetes API servers. It provides the machinery for installing API resources as HTTP endpoints and handling CRUD operations.

## Purpose

The endpoints package:
- **API Installation**: Registers API resources as HTTP endpoints
- **Request Routing**: Routes requests to appropriate handlers
- **Content Negotiation**: Handles multiple serialization formats
- **Discovery**: Provides API discovery endpoints
- **Handlers**: Implements standard REST operations (GET, LIST, CREATE, UPDATE, PATCH, DELETE)

## Architecture

```mermaid
graph TB
    A[APIGroupVersion] --> B[APIInstaller]
    B --> C[Install Resources]
    C --> D[Create Routes]
    D --> E[Register Handlers]
    E --> F[HTTP Endpoints]
    
    style B fill:#e6f3ff
    style E fill:#fff4e6
    style F fill:#e6ffe6
```

## Key Components

### APIInstaller

Installs API resources as HTTP endpoints:

```mermaid
classDiagram
    class APIInstaller {
        +group *APIGroupVersion
        +prefix string
        +minRequestTimeout time.Duration
        +Install() []*restful.WebService
    }
    
    class APIGroupVersion {
        +Storage map[string]rest.Storage
        +Root string
        +GroupVersion schema.GroupVersion
        +Serializer runtime.NegotiatedSerializer
    }
    
    APIInstaller --> APIGroupVersion
```

### Request Handlers

Located in `handlers/`:

```
pkg/endpoints/handlers/
├── create.go           # CREATE handler
├── delete.go           # DELETE handler
├── get.go              # GET handler
├── patch.go            # PATCH handler
├── update.go           # UPDATE handler
├── watch.go            # WATCH handler
├── responsewriters.go  # Response writing
├── negotiation/        # Content negotiation
├── fieldmanager/       # Server-side apply
└── metrics/            # Handler metrics
```

## REST Operations

### Standard Verbs

```mermaid
graph LR
    A[REST Storage] --> B[GET]
    A --> C[LIST]
    A --> D[CREATE]
    A --> E[UPDATE]
    A --> F[PATCH]
    A --> G[DELETE]
    A --> H[WATCH]
    A --> I[DELETECOLLECTION]
    
    style A fill:#e6f3ff
```

### URL Patterns

| Operation | URL Pattern | Example |
|-----------|-------------|---------|
| GET | `/apis/{group}/{version}/namespaces/{ns}/{resource}/{name}` | `/apis/apps/v1/namespaces/default/deployments/nginx` |
| LIST | `/apis/{group}/{version}/namespaces/{ns}/{resource}` | `/apis/apps/v1/namespaces/default/deployments` |
| CREATE | `/apis/{group}/{version}/namespaces/{ns}/{resource}` | POST to `/apis/apps/v1/namespaces/default/deployments` |
| UPDATE | `/apis/{group}/{version}/namespaces/{ns}/{resource}/{name}` | PUT to `/apis/apps/v1/namespaces/default/deployments/nginx` |
| PATCH | `/apis/{group}/{version}/namespaces/{ns}/{resource}/{name}` | PATCH to `/apis/apps/v1/namespaces/default/deployments/nginx` |
| DELETE | `/apis/{group}/{version}/namespaces/{ns}/{resource}/{name}` | DELETE to `/apis/apps/v1/namespaces/default/deployments/nginx` |
| WATCH | `/apis/{group}/{version}/watch/namespaces/{ns}/{resource}` | `/apis/apps/v1/watch/namespaces/default/deployments` |

## Discovery

Located in `discovery/`:

```mermaid
graph TB
    A[Discovery] --> B["/api"]
    A --> C["/apis"]
    A --> D["/apis/{group}"]
    A --> E["/apis/{group}/{version}"]
    
    B --> F[Core API Groups]
    C --> G[API Group List]
    D --> H[Group Versions]
    E --> I[Resource List]
    
    style A fill:#e6f3ff
```

### Aggregated Discovery

V2 discovery format provides efficient aggregated discovery:
- Single endpoint for all resources
- Includes subresources
- Reduced API calls

## Content Negotiation

Located in `handlers/negotiation/`:

Supports multiple serialization formats:
- **JSON**: Default format
- **YAML**: Human-readable
- **Protobuf**: Efficient binary format

```mermaid
graph LR
    A[Accept Header] --> B[Negotiator]
    B --> C{Format?}
    C -->|JSON| D[JSON Serializer]
    C -->|YAML| E[YAML Serializer]
    C -->|Protobuf| F[Protobuf Serializer]
    
    style B fill:#e6f3ff
```

## Filters

Located in `filters/`:

```
pkg/endpoints/filters/
├── audit.go            # Audit logging
├── authentication.go   # Authentication
├── authorization.go    # Authorization
├── cors.go             # CORS headers
├── impersonation.go    # User impersonation
├── maxinflight.go      # Concurrency limiting
├── requestinfo.go      # Request info extraction
├── timeout.go          # Request timeouts
├── trace.go            # Distributed tracing
└── warning.go          # Warning headers
```

## Package Structure

```
pkg/endpoints/
├── installer.go        # API installer
├── groupversion.go     # API group version
├── handlers/           # Request handlers
├── discovery/          # API discovery
├── filters/            # HTTP filters
├── metrics/            # Endpoint metrics
├── openapi/            # OpenAPI generation
├── request/            # Request context
└── warning/            # Warning system
```

## Related Packages
- **pkg/registry**: Provides REST storage implementations
- **pkg/server**: Integrates endpoints into server
- **pkg/admission**: Called by handlers
