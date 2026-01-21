# pkg/audit - Audit Logging System

## Overview

The `pkg/audit` package implements the audit logging system for Kubernetes API servers. It provides a policy-driven event logging pipeline that records API requests for security, compliance, and debugging purposes.

## Purpose

The audit system:
- **Records API Activity**: Logs all API requests with configurable detail levels
- **Policy-Based Filtering**: Controls what gets logged based on user, resource, verb, etc.
- **Multiple Backends**: Supports various storage backends (log files, webhooks, etc.)
- **Performance Optimized**: Minimizes impact on API server performance
- **Compliance Support**: Provides audit trail for regulatory requirements

## Architecture

```mermaid
graph TB
    subgraph "Request Flow"
        A[API Request] --> B[Handler Chain]
        B --> C[Audit Filter]
    end
    
    subgraph "Audit Pipeline"
        C --> D[Policy Evaluator]
        D --> E{Level?}
        E -->|None| F[Skip]
        E -->|Metadata| G[Create Event]
        E -->|Request| G
        E -->|RequestResponse| G
        G --> H[Event Decorator]
        H --> I[Backend]
    end
    
    subgraph "Backends"
        I --> J[Log Backend]
        I --> K[Webhook Backend]
        I --> L[Dynamic Backend]
    end
    
    style D fill:#e6f3ff
    style G fill:#fff4e6
    style I fill:#ffe6e6
```

## Core Interfaces

### Backend Interface

The main interface for audit backends:

```go
type Backend interface {
    Sink
    Run(stopCh <-chan struct{}) error
    Shutdown()
    String() string
}

type Sink interface {
    ProcessEvents(events ...*auditinternal.Event) bool
}
```

**Methods**:
- **ProcessEvents**: Process audit events (may be called up to 3 times per request)
- **Run**: Initialize backend (non-blocking)
- **Shutdown**: Gracefully shut down, ensuring all events are delivered
- **String**: Return backend name

### PolicyRuleEvaluator Interface

Evaluates audit policy against requests:

```go
type PolicyRuleEvaluator interface {
    EvaluatePolicyRule(authorizer.Attributes) RequestAuditConfig
}
```

**Returns**:
- **Level**: Audit level for this request
- **OmitStages**: Stages to skip
- **OmitManagedFields**: Whether to omit managed fields

## Audit Levels

```mermaid
graph LR
    A[None] -->|No logging| B[Metadata]
    B -->|+ Request body| C[Request]
    C -->|+ Response body| D[RequestResponse]
    
    style A fill:#f9f9f9
    style B fill:#e6f3ff
    style C fill:#fff4e6
    style D fill:#ffe6e6
```

### Level Details

| Level | What's Logged | Use Case |
|-------|---------------|----------|
| **None** | Nothing | Exclude from audit |
| **Metadata** | Request metadata only | Most requests |
| **Request** | Metadata + request body | Write operations |
| **RequestResponse** | Metadata + request + response | Debugging, compliance |

**Metadata includes**:
- User information
- Timestamp
- Resource (group, version, resource, namespace, name)
- Verb (get, list, create, update, patch, delete, etc.)
- HTTP status code
- Source IPs
- User agent

## Audit Stages

Events can be logged at different stages of request processing:

```mermaid
sequenceDiagram
    participant Client
    participant Handler
    participant Admission
    participant Storage
    
    Client->>Handler: Request
    Note over Handler: Stage: RequestReceived
    Handler->>Admission: Validate
    Admission->>Storage: Persist
    Storage-->>Handler: Success
    Note over Handler: Stage: ResponseStarted
    Handler-->>Client: Headers
    Note over Handler: Stage: ResponseComplete
    Handler-->>Client: Body
```

**Stages**:
- **RequestReceived**: Request received, before handler chain
- **ResponseStarted**: Response headers sent
- **ResponseComplete**: Response body sent (normal completion)
- **Panic**: Handler panicked

## Event Structure

```mermaid
classDiagram
    class Event {
        +Level Level
        +AuditID types.UID
        +Stage Stage
        +RequestURI string
        +Verb string
        +User UserInfo
        +ImpersonatedUser *UserInfo
        +SourceIPs []string
        +UserAgent string
        +ObjectRef *ObjectReference
        +ResponseStatus *metav1.Status
        +RequestObject *runtime.Unknown
        +ResponseObject *runtime.Unknown
        +RequestReceivedTimestamp metav1.MicroTime
        +StageTimestamp metav1.MicroTime
        +Annotations map[string]string
    }
    
    class ObjectReference {
        +Resource string
        +Namespace string
        +Name string
        +UID types.UID
        +APIGroup string
        +APIVersion string
        +ResourceVersion string
        +Subresource string
    }
    
    Event --> ObjectReference
```

## Policy Evaluation

### Policy Structure

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
# Don't log read-only requests
- level: None
  verbs: ["get", "list", "watch"]
  
# Log secrets at metadata level
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets"]
    
# Log all write operations with request body
- level: Request
  verbs: ["create", "update", "patch", "delete"]
  
# Catch-all rule
- level: Metadata
```

### Policy Matching

```mermaid
graph TB
    A[Request] --> B{Match Rule 1?}
    B -->|Yes| C[Apply Rule 1]
    B -->|No| D{Match Rule 2?}
    D -->|Yes| E[Apply Rule 2]
    D -->|No| F{Match Rule N?}
    F -->|Yes| G[Apply Rule N]
    F -->|No| H[No Audit]
    
    style C fill:#e6ffe6
    style E fill:#e6ffe6
    style G fill:#e6ffe6
    style H fill:#f9f9f9
```

**Matching Order**:
1. Rules are evaluated in order
2. First matching rule wins
3. If no rule matches, event is not logged

**Match Criteria**:
- **Users**: User names
- **UserGroups**: User group memberships
- **Verbs**: HTTP verbs or Kubernetes verbs
- **Resources**: API resources (group/version/resource)
- **Namespaces**: Namespace names
- **NonResourceURLs**: Non-resource URL paths

## Backends

### Log Backend

Writes events to log files:

```mermaid
graph LR
    A[Events] --> B[Format]
    B --> C[Buffer]
    C --> D[Write to File]
    D --> E[Rotate]
    
    style B fill:#e6f3ff
    style C fill:#fff4e6
    style D fill:#e6ffe6
```

**Features**:
- JSON format (one event per line)
- Buffered writes for performance
- Log rotation support
- Configurable batch size

### Webhook Backend

Sends events to external webhook:

```mermaid
sequenceDiagram
    participant Audit
    participant Buffer
    participant Webhook
    participant External
    
    Audit->>Buffer: Add Event
    Buffer->>Buffer: Batch Events
    Buffer->>Webhook: Send Batch
    Webhook->>External: HTTP POST
    External-->>Webhook: 200 OK
    Webhook-->>Buffer: Success
```

**Features**:
- Batching for efficiency
- Retry on failure
- Configurable timeout
- TLS support

### Dynamic Backend

Routes events to multiple backends:

```mermaid
graph TB
    A[Event] --> B[Dynamic Backend]
    B --> C[Backend 1]
    B --> D[Backend 2]
    B --> E[Backend N]
    
    style B fill:#fff4e6
```

**Features**:
- Multiple backend support
- Dynamic backend registration
- Parallel event delivery

## Event Decorators

### Audit Annotations

Admission plugins can add annotations to events:

```go
// In admission plugin
attributes.AddAnnotation(
    "podsecuritypolicy.admission.k8s.io/policy",
    "restricted",
)
```

Annotations appear in the audit event:

```json
{
  "annotations": {
    "podsecuritypolicy.admission.k8s.io/policy": "restricted"
  }
}
```

### Impersonation

Tracks impersonation information:

```json
{
  "user": {
    "username": "admin",
    "groups": ["system:masters"]
  },
  "impersonatedUser": {
    "username": "developer",
    "groups": ["developers"]
  }
}
```

## Context Integration

### Audit Context

Audit information is stored in request context:

```go
// Store audit ID in context
ctx = audit.WithAuditID(ctx, auditID)

// Retrieve audit ID
auditID := audit.AuditIDFrom(ctx)

// Store audit event
ctx = audit.WithAuditEvent(ctx, event)

// Retrieve audit event
event := audit.AuditEventFrom(ctx)
```

### Request Attributes

Audit uses authorization attributes:

```mermaid
graph LR
    A[Request] --> B[Extract Attributes]
    B --> C[Authorization]
    B --> D[Audit]
    
    style B fill:#e6f3ff
    style C fill:#fff4e6
    style D fill:#fff4e6
```

## Performance Considerations

### Buffering

```mermaid
graph TB
    A[Event 1] --> B[Buffer]
    C[Event 2] --> B
    D[Event N] --> B
    B --> E{Buffer Full?}
    E -->|Yes| F[Flush]
    E -->|No| G[Wait]
    F --> H[Backend]
    
    style B fill:#fff4e6
    style F fill:#ffe6e6
```

**Buffering Strategy**:
- Events buffered in memory
- Flush on buffer full or timeout
- Batch size configurable
- Reduces backend calls

### Asynchronous Processing

```mermaid
sequenceDiagram
    participant Handler
    participant Audit
    participant Backend
    
    Handler->>Audit: Log Event
    Audit->>Audit: Queue Event
    Audit-->>Handler: Return Immediately
    
    par Background Processing
        Audit->>Backend: Process Event
    end
```

**Benefits**:
- Non-blocking API requests
- Minimal latency impact
- Batch processing efficiency

## Metrics

The audit system exposes metrics:

```mermaid
graph LR
    A[Metrics] --> B[Events Total]
    A --> C[Events Dropped]
    A --> D[Backend Latency]
    A --> E[Buffer Size]
    
    style A fill:#e6f3ff
```

**Key Metrics**:
- `apiserver_audit_event_total`: Total events generated
- `apiserver_audit_requests_rejected_total`: Rejected due to errors
- `apiserver_audit_level_total`: Events per level
- Backend-specific latency and error metrics

## Union Backend

Combines multiple backends:

```go
type Union struct {
    backends []Backend
}

func (u *Union) ProcessEvents(events ...*Event) bool {
    success := true
    for _, backend := range u.backends {
        if !backend.ProcessEvents(events...) {
            success = false
        }
    }
    return success
}
```

**Use Case**: Send events to both log file and webhook

## Request Logging

### Request Object

Captures full request details:

```go
type Request struct {
    *auditinternal.Event
    
    // Additional request-specific fields
    RequestObject runtime.Object
    ResponseObject runtime.Object
}
```

### Truncation

Large objects may be truncated:

```mermaid
graph TB
    A[Object] --> B{Size Check}
    B -->|Small| C[Include Full]
    B -->|Large| D[Truncate]
    D --> E[Add Truncation Note]
    
    style D fill:#ffe6e6
    style E fill:#fff4e6
```

**Truncation Rules**:
- Objects over size limit are truncated
- Truncation is noted in event
- Prevents excessive log size

## Package Structure

```
pkg/audit/
├── types.go              # Backend and evaluator interfaces
├── context.go            # Context integration
├── evaluator.go          # Policy evaluation
├── request.go            # Request logging
├── request_log.go        # Request log formatter
├── format.go             # Event formatting
├── metrics.go            # Metrics collection
├── scheme.go             # Scheme registration
├── union.go              # Union backend
└── policy/               # Policy evaluation
    ├── checker.go        # Policy rule checker
    ├── reader.go         # Policy file reader
    ├── enforcer.go       # Policy enforcement
    └── util.go           # Utility functions
```

## Configuration Example

### Complete Audit Configuration

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
# Don't log requests to certain non-resource URLs
- level: None
  nonResourceURLs:
  - /healthz*
  - /version
  - /swagger*

# Don't log watch requests
- level: None
  verbs: ["watch"]

# Don't log authenticated requests to certain non-resource URLs
- level: None
  userGroups: ["system:authenticated"]
  nonResourceURLs:
  - /api*

# Log pod changes at RequestResponse level
- level: RequestResponse
  resources:
  - group: ""
    resources: ["pods"]
  verbs: ["create", "update", "patch", "delete"]

# Log secrets and configmaps at Metadata level
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]

# Log all other resources at Request level
- level: Request
  omitStages:
  - RequestReceived
```

## Best Practices

### 1. Policy Design

**Start restrictive, then expand**:
```yaml
# Start with this
- level: Metadata

# Add specific rules as needed
- level: Request
  resources:
  - group: "apps"
    resources: ["deployments"]
```

### 2. Performance

**Minimize RequestResponse level**:
- Only use for critical resources
- Exclude read-only operations
- Use omitStages to reduce events

### 3. Storage

**Plan for log volume**:
- Estimate events per second
- Configure log rotation
- Consider external storage

### 4. Security

**Protect audit logs**:
- Restrict file permissions
- Use separate storage
- Enable encryption

### 5. Compliance

**Meet regulatory requirements**:
- Log all access to sensitive data
- Retain logs for required period
- Ensure log integrity

## Integration with API Server

### Handler Chain Integration

```mermaid
sequenceDiagram
    participant Request
    participant Audit Filter
    participant Evaluator
    participant Handler
    participant Backend
    
    Request->>Audit Filter: HTTP Request
    Audit Filter->>Evaluator: Evaluate Policy
    Evaluator-->>Audit Filter: Audit Config
    Audit Filter->>Backend: Log (RequestReceived)
    Audit Filter->>Handler: Continue
    Handler-->>Audit Filter: Response
    Audit Filter->>Backend: Log (ResponseComplete)
    Audit Filter-->>Request: HTTP Response
```

### Server Configuration

```go
// In server config
config := &server.Config{
    AuditBackend: auditBackend,
    AuditPolicyRuleEvaluator: policyEvaluator,
}
```

## Testing

### Mock Backend

```go
type fakeBackend struct {
    events []*auditinternal.Event
}

func (f *fakeBackend) ProcessEvents(events ...*auditinternal.Event) bool {
    f.events = append(f.events, events...)
    return true
}
```

### Testing Policies

```go
// Create test policy
policy := &audit.Policy{
    Rules: []audit.PolicyRule{
        {
            Level: audit.LevelMetadata,
            Resources: []audit.GroupResources{
                {Resources: []string{"pods"}},
            },
        },
    },
}

// Evaluate
config := evaluator.EvaluatePolicyRule(attributes)
assert.Equal(t, audit.LevelMetadata, config.Level)
```

## Related Packages

- **pkg/apis/audit**: Audit event type definitions
- **pkg/admission**: Admission plugins add annotations
- **pkg/authorization**: Provides request attributes
- **pkg/server**: Integrates audit into handler chain

## References

- [Kubernetes Auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)
- [Audit Policy](https://kubernetes.io/docs/reference/config-api/apiserver-audit.v1/)
- [Audit Annotations](https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/#audit-annotations)
