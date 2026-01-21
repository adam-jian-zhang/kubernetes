# k8s.io/apiserver Documentation

Comprehensive documentation for the Kubernetes API server library (`k8s.io/apiserver`).

## Overview

The `k8s.io/apiserver` library is the foundational framework for building Kubernetes-style API servers. It provides the complete machinery for creating aggregated API servers with delegated authentication and authorization, kubectl-compatible discovery, admission control chains, and versioned types.

## Documentation Structure

### Getting Started

- **[00-overview.md](./00-overview.md)** - High-level architecture and design principles
  - Server composition and request flow
  - Core components and extension patterns
  - Package organization

### Core Packages

#### Request Processing Pipeline

1. **[04-authentication.md](./04-authentication.md)** - Authentication Framework
   - User identification
   - Multiple authenticator types (X.509, OIDC, tokens, etc.)
   - Service account tokens

2. **[05-authorization.md](./05-authorization.md)** - Authorization Framework
   - Access control decisions
   - RBAC, Node, Webhook authorization
   - Rule resolution

3. **[01-admission.md](./01-admission.md)** - Admission Control
   - Mutation and validation plugins
   - Webhook admission
   - CEL admission policies

#### API Server Core

4. **[12-server.md](./12-server.md)** - GenericAPIServer
   - Server lifecycle management
   - Handler chain construction
   - API group installation
   - Health checks and hooks

5. **[07-endpoints.md](./07-endpoints.md)** - REST Endpoints
   - API installation and routing
   - Request handlers (GET, LIST, CREATE, UPDATE, PATCH, DELETE, WATCH)
   - Discovery endpoints
   - Content negotiation

6. **[11-registry.md](./11-registry.md)** - Storage Registry
   - REST storage implementation
   - Strategy pattern for business logic
   - CRUD operations
   - Subresource handling

7. **[13-storage.md](./13-storage.md)** - Storage Layer
   - Storage interface and implementations
   - Watch cache for performance
   - Encryption at rest
   - Optimistic concurrency

#### Supporting Systems

8. **[03-audit.md](./03-audit.md)** - Audit Logging
   - Policy-driven event logging
   - Multiple backends (log, webhook)
   - Audit levels and stages

9. **[02-apis.md](./02-apis.md)** - Internal API Types
   - Configuration types
   - Admission, audit, encryption configuration
   - API discovery types

10. **[06-cel.md](./06-cel.md)** - CEL Support
    - Common Expression Language integration
    - Validation and admission policies
    - Expression compilation and evaluation

#### Utilities and Features

11. **[08-features.md](./08-features.md)** - Feature Gates
    - Feature lifecycle (alpha, beta, GA)
    - Feature gate definitions

12. **[09-quota.md](./09-quota.md)** - Resource Quota
    - Quota evaluation
    - Resource usage calculation

13. **[10-reconcilers.md](./10-reconcilers.md)** - Reconciliation
    - Lease management
    - State synchronization

14. **[14-storageversion.md](./14-storageversion.md)** - Storage Version
    - Version tracking
    - Migration support

15. **[15-util.md](./15-util.md)** - Utilities
    - Flow control (priority and fairness)
    - Webhook utilities
    - Feature gate utilities

16. **[16-validation.md](./16-validation.md)** - Validation Metrics
    - Validation performance tracking
    - CEL evaluation metrics

17. **[17-warning.md](./17-warning.md)** - Warning Headers
    - HTTP warning support
    - Deprecation notices
    - Client communication

## Quick Navigation by Use Case

### Building a Custom API Server

1. Start with [00-overview.md](./00-overview.md) for architecture
2. Review [12-server.md](./12-server.md) for GenericAPIServer
3. Study [07-endpoints.md](./07-endpoints.md) for API installation
4. Understand [11-registry.md](./11-registry.md) for storage
5. Learn [13-storage.md](./13-storage.md) for persistence

### Implementing Admission Control

1. Read [01-admission.md](./01-admission.md) for framework
2. Check [06-cel.md](./06-cel.md) for CEL policies
3. Review [17-warning.md](./17-warning.md) for warnings

### Understanding Request Flow

1. [04-authentication.md](./04-authentication.md) - Who is the user?
2. [05-authorization.md](./05-authorization.md) - What can they do?
3. [01-admission.md](./01-admission.md) - Is the request valid?
4. [07-endpoints.md](./07-endpoints.md) - Handle the request
5. [03-audit.md](./03-audit.md) - Log the activity

### Storage and Persistence

1. [13-storage.md](./13-storage.md) - Storage interface
2. [11-registry.md](./11-registry.md) - REST storage
3. [14-storageversion.md](./14-storageversion.md) - Version management

## Architecture Diagrams

Throughout the documentation, you'll find Mermaid diagrams illustrating:
- Request flow through the server
- Component interactions
- Data flow and transformations
- Lifecycle and state machines

## Key Concepts

### Server Chain

The Kubernetes API server is composed of three servers:
1. **Aggregator Server** - Routes to extension API servers
2. **Kube API Server** - Serves core Kubernetes APIs
3. **API Extensions Server** - Handles CustomResourceDefinitions

### Handler Chain

Every request flows through a standard chain:
1. Authentication - Identify the user
2. Authorization - Check permissions
3. Priority & Fairness - Manage concurrency
4. Admission - Validate and mutate
5. REST Handler - Execute operation

### Storage Layers

Three layers abstract storage:
1. **REST Storage** - REST interface for resources
2. **Registry** - Business logic and strategies
3. **Storage Interface** - Backend abstraction (etcd)

## Extension Patterns

The apiserver supports multiple extension patterns:

1. **CustomResourceDefinitions (CRDs)** - Declarative, no code
2. **API Aggregation** - Full control, custom logic
3. **Admission Webhooks** - External policy enforcement
4. **Built-in Admission Plugins** - Compiled into server

## Design Principles

- **Composability** - Server chain allows layering
- **Pluggability** - Authentication, authorization, admission are pluggable
- **Extensibility** - Multiple extension patterns
- **Performance** - Watch cache and efficient operations
- **Consistency** - Optimistic concurrency and strong guarantees
- **Security** - Defense in depth
- **Observability** - Comprehensive metrics and tracing

## Implementation Notes

### Code Generation

Many types use code generators:
- `deepcopy-gen` - DeepCopy methods
- `conversion-gen` - Version conversion
- `defaulter-gen` - Default values
- `openapi-gen` - OpenAPI specifications

### Testing

Each package includes:
- Unit tests
- Integration tests
- Mock implementations
- Testing utilities

### Metrics

All major components expose Prometheus metrics:
- Request latency
- Error rates
- Resource usage
- Queue depths

## References

### Official Documentation

- [Kubernetes API Concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/)
- [API Aggregation](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/apiserver-aggregation/)
- [Custom Resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)
- [Admission Controllers](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)

### Source Code

- [GitHub Repository](https://github.com/kubernetes/kubernetes/tree/master/staging/src/k8s.io/apiserver)
- [API Conventions](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md)

## Contributing

This documentation is generated from the actual implementation in `staging/src/k8s.io/apiserver`. 

**Note**: There are NO compatibility guarantees for this repository. It is in direct support of Kubernetes, so branches track Kubernetes versions.

## Version

This documentation corresponds to the Kubernetes apiserver library as of the analysis date. For the most current information, refer to the source code and official Kubernetes documentation.

---

**Navigation**: Start with [00-overview.md](./00-overview.md) for a high-level introduction, then explore specific packages based on your needs.
