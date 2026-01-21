# pkg/authentication - Authentication Framework

## Overview

The `pkg/authentication` package provides the authentication framework for Kubernetes API servers. It identifies users making API requests through a pluggable system of authenticators.

## Purpose

The authentication system:
- **Identifies Users**: Determines who is making the request
- **Pluggable Architecture**: Supports multiple authentication methods
- **Union Strategy**: Tries authenticators in sequence until one succeeds
- **Token Management**: Handles various token formats (JWT, bootstrap tokens, etc.)
- **Service Account Support**: Built-in support for Kubernetes service accounts

## Architecture

```mermaid
graph TB
    subgraph "Request Flow"
        A[HTTP Request] --> B[Authentication Handler]
    end
    
    subgraph "Authenticator Chain"
        B --> C[Authenticator 1]
        C -->|Failed| D[Authenticator 2]
        D -->|Failed| E[Authenticator N]
        C -->|Success| F[User Info]
        D -->|Success| F
        E -->|Success| F
        E -->|Failed| G[Anonymous]
    end
    
    subgraph "User Context"
        F --> H[Add to Context]
        G --> H
        H --> I[Authorization]
    end
    
    style C fill:#e6f3ff
    style F fill:#e6ffe6
    style G fill:#fff4e6
```

## Core Interfaces

### Authenticator Interfaces

```go
// Token authenticator - validates bearer tokens
type Token interface {
    AuthenticateToken(ctx context.Context, token string) (*Response, bool, error)
}

// Request authenticator - validates HTTP requests
type Request interface {
    AuthenticateRequest(req *http.Request) (*Response, bool, error)
}
```

### Authentication Response

```mermaid
classDiagram
    class Response {
        +Audiences Audiences
        +User user.Info
    }
    
    class UserInfo {
        +GetName() string
        +GetUID() string
        +GetGroups() []string
        +GetExtra() map[string][]string
    }
    
    Response --> UserInfo
```

**Response Fields**:
- **Audiences**: Token audiences (for audience-aware authenticators)
- **User**: User information
  - **Name**: Username
  - **UID**: Unique identifier
  - **Groups**: Group memberships
  - **Extra**: Additional attributes

## Built-in Authenticators

### 1. X509 Client Certificates

Located in `request/x509/`:

```mermaid
graph LR
    A[TLS Handshake] --> B[Extract Client Cert]
    B --> C[Verify Certificate]
    C --> D[Extract User Info]
    D --> E[Response]
    
    style C fill:#e6f3ff
    style D fill:#fff4e6
```

**User Mapping**:
- **Username**: Certificate CommonName (CN)
- **Groups**: Certificate Organization (O) fields
- **UID**: Not set

**Example Certificate**:
```
Subject: CN=john, O=developers, O=team-a
```
Maps to:
- Username: `john`
- Groups: `["developers", "team-a"]`

### 2. Bearer Tokens

Located in `request/bearertoken/`:

```mermaid
graph LR
    A[Authorization Header] --> B[Extract Token]
    B --> C[Token Authenticator]
    C --> D[Validate]
    D --> E[User Info]
    
    style B fill:#e6f3ff
    style D fill:#fff4e6
```

**Header Format**:
```
Authorization: Bearer <token>
```

**Token Types**:
- Service account tokens (JWT)
- Bootstrap tokens
- OIDC tokens
- Static tokens
- Webhook tokens

### 3. Service Account Tokens

Located in `serviceaccount/`:

```mermaid
sequenceDiagram
    participant Client
    participant Authenticator
    participant TokenValidator
    participant APIServer
    
    Client->>Authenticator: JWT Token
    Authenticator->>TokenValidator: Validate Signature
    TokenValidator->>TokenValidator: Check Expiry
    TokenValidator->>TokenValidator: Verify Audience
    TokenValidator->>APIServer: Lookup ServiceAccount
    APIServer-->>TokenValidator: SA Found
    TokenValidator-->>Authenticator: Valid
    Authenticator-->>Client: User Info
```

**JWT Claims**:
```json
{
  "iss": "https://kubernetes.default.svc",
  "sub": "system:serviceaccount:default:my-sa",
  "aud": ["https://kubernetes.default.svc"],
  "exp": 1234567890,
  "iat": 1234567800,
  "kubernetes.io": {
    "namespace": "default",
    "serviceaccount": {
      "name": "my-sa",
      "uid": "12345"
    },
    "pod": {
      "name": "my-pod",
      "uid": "67890"
    }
  }
}
```

**User Mapping**:
- **Username**: `system:serviceaccount:<namespace>:<name>`
- **UID**: ServiceAccount UID
- **Groups**: 
  - `system:serviceaccounts`
  - `system:serviceaccounts:<namespace>`

### 4. OIDC (OpenID Connect)

Located in `token/oidc/`:

```mermaid
sequenceDiagram
    participant Client
    participant APIServer
    participant OIDC Provider
    
    Client->>OIDC Provider: Authenticate
    OIDC Provider-->>Client: ID Token
    Client->>APIServer: Request + ID Token
    APIServer->>OIDC Provider: Fetch JWKS
    OIDC Provider-->>APIServer: Public Keys
    APIServer->>APIServer: Verify Token
    APIServer-->>Client: Authorized
```

**Configuration**:
- **Issuer URL**: OIDC provider URL
- **Client ID**: Expected audience
- **CA Bundle**: Provider's CA certificate
- **Username Claim**: Claim for username (default: `sub`)
- **Groups Claim**: Claim for groups (optional)

**User Mapping**:
- **Username**: From configured claim (e.g., `email`, `sub`)
- **Groups**: From configured groups claim
- **Extra**: Additional claims as extra attributes

### 5. Webhook Token Authentication

Located in `token/webhook/`:

```mermaid
sequenceDiagram
    participant Client
    participant APIServer
    participant Webhook
    
    Client->>APIServer: Request + Token
    APIServer->>Webhook: TokenReview
    Note over Webhook: Validate Token
    Webhook-->>APIServer: TokenReview Response
    APIServer-->>Client: Authorized/Denied
```

**TokenReview Request**:
```json
{
  "apiVersion": "authentication.k8s.io/v1",
  "kind": "TokenReview",
  "spec": {
    "token": "<bearer-token>",
    "audiences": ["https://kubernetes.default.svc"]
  }
}
```

**TokenReview Response**:
```json
{
  "apiVersion": "authentication.k8s.io/v1",
  "kind": "TokenReview",
  "status": {
    "authenticated": true,
    "user": {
      "username": "jane",
      "uid": "12345",
      "groups": ["developers", "team-b"]
    },
    "audiences": ["https://kubernetes.default.svc"]
  }
}
```

### 6. Bootstrap Tokens

Located in `token/bootstrap/`:

```mermaid
graph LR
    A[Bootstrap Token] --> B[Format Check]
    B --> C[Secret Lookup]
    C --> D[Validate Expiry]
    D --> E[Check Usage]
    E --> F[User Info]
    
    style B fill:#e6f3ff
    style D fill:#fff4e6
```

**Token Format**: `<token-id>.<token-secret>`
- Token ID: 6 characters
- Token Secret: 16 characters

**Use Cases**:
- Node bootstrapping
- Temporary cluster access
- Automated provisioning

**User Mapping**:
- **Username**: `system:bootstrap:<token-id>`
- **Groups**: Configured in token secret

### 7. Anonymous Authentication

Located in `request/anonymous/`:

```mermaid
graph LR
    A[No Auth Info] --> B[Anonymous Authenticator]
    B --> C[Anonymous User]
    
    style C fill:#fff4e6
```

**Anonymous User**:
- **Username**: `system:anonymous`
- **Groups**: `["system:unauthenticated"]`

**Use Case**: Public endpoints (e.g., `/healthz`, `/version`)

## Authenticator Factory

Located in `authenticatorfactory/`:

```mermaid
graph TB
    A[Config] --> B[Authenticator Factory]
    B --> C[Create X509]
    B --> D[Create Token]
    B --> E[Create Request]
    C --> F[Union Authenticator]
    D --> F
    E --> F
    
    style B fill:#e6f3ff
    style F fill:#fff4e6
```

**Factory Pattern**:
```go
type Config struct {
    Anonymous bool
    ClientCAContentProvider CAContentProvider
    TokenAuthFile string
    OIDCIssuerURL string
    WebhookTokenAuthnConfigFile string
    ServiceAccountKeyFiles []string
    // ... more config
}

func (config Config) New() (authenticator.Request, error) {
    var authenticators []authenticator.Request
    
    // Add X509 authenticator
    if config.ClientCAContentProvider != nil {
        authenticators = append(authenticators, x509Authenticator)
    }
    
    // Add token authenticators
    tokenAuthenticators := []authenticator.Token{}
    // ... add various token authenticators
    
    // Combine into union
    return union.New(authenticators...), nil
}
```

## Union Authenticator

Located in `request/union/`:

```mermaid
sequenceDiagram
    participant Request
    participant Union
    participant Auth1
    participant Auth2
    participant AuthN
    
    Request->>Union: Authenticate
    Union->>Auth1: Try First
    Auth1-->>Union: Failed
    Union->>Auth2: Try Second
    Auth2-->>Union: Success
    Union-->>Request: User Info
```

**Strategy**:
- Try each authenticator in order
- Return on first success
- Return error only if all fail

## User Information

### User Interface

```go
type Info interface {
    GetName() string
    GetUID() string
    GetGroups() []string
    GetExtra() map[string][]string
}
```

### Default User

```go
type DefaultInfo struct {
    Name   string
    UID    string
    Groups []string
    Extra  map[string][]string
}
```

### Special Users

```mermaid
graph TB
    A[Special Users] --> B[system:anonymous]
    A --> C[system:apiserver]
    A --> D[system:kube-controller-manager]
    A --> E[system:kube-scheduler]
    A --> F[system:kube-proxy]
    A --> G[system:node:*]
    A --> H[system:serviceaccount:*]
    
    style A fill:#e6f3ff
```

## Group Mapping

Located in `group/`:

```mermaid
graph LR
    A[Authenticated User] --> B[Group Adder]
    B --> C[Add system:authenticated]
    C --> D[Add Custom Groups]
    D --> E[Final User Info]
    
    style B fill:#e6f3ff
    style C fill:#fff4e6
```

**Automatic Groups**:
- `system:authenticated`: All authenticated users
- `system:unauthenticated`: Anonymous users

## CEL Authentication

Located in `cel/`:

Supports CEL expressions for authentication decisions:

```yaml
apiVersion: authentication.k8s.io/v1alpha1
kind: AuthenticationConfiguration
jwt:
- issuer:
    url: https://issuer.example.com
    audiences:
    - my-app
  claimMappings:
    username:
      expression: 'claims.email'
    groups:
      expression: 'claims.groups'
  claimValidationRules:
  - expression: 'claims.exp > now'
    message: "token is expired"
```

## Request Decorators

### Header Authenticator

Located in `request/headerrequest/`:

Extracts user info from HTTP headers:

```
X-Remote-User: john
X-Remote-Group: developers
X-Remote-Group: team-a
```

**Use Case**: Reverse proxy authentication

### Union Authenticator

Combines multiple request authenticators:

```go
authenticator := union.New(
    x509Authenticator,
    bearerTokenAuthenticator,
    basicAuthAuthenticator,
)
```

## Caching

### Cache Authenticator

Located in `token/cache/`:

```mermaid
graph TB
    A[Token] --> B{In Cache?}
    B -->|Yes| C[Return Cached]
    B -->|No| D[Authenticate]
    D --> E[Store in Cache]
    E --> F[Return Result]
    
    style B fill:#e6f3ff
    style E fill:#fff4e6
```

**Features**:
- TTL-based expiration
- Success and failure caching
- Reduces authenticator load

**Configuration**:
- Cache size
- Success TTL
- Failure TTL

## Package Structure

```
pkg/authentication/
├── authenticator/        # Core interfaces
│   └── interfaces.go
├── authenticatorfactory/ # Factory for building authenticators
│   └── delegating.go
├── request/              # Request-based authenticators
│   ├── anonymous/        # Anonymous authenticator
│   ├── bearertoken/      # Bearer token extraction
│   ├── headerrequest/    # Header-based auth
│   ├── union/            # Union authenticator
│   ├── websocket/        # WebSocket auth
│   └── x509/             # Client certificate auth
├── token/                # Token-based authenticators
│   ├── cache/            # Token caching
│   ├── oidc/             # OIDC authenticator
│   ├── webhook/          # Webhook token auth
│   └── bootstrap/        # Bootstrap tokens
├── serviceaccount/       # Service account tokens
│   └── jwt.go
├── group/                # Group mapping
│   └── group_adder.go
├── cel/                  # CEL expression support
│   └── compiler.go
└── user/                 # User info types
    └── user.go
```

## Integration with API Server

### Handler Chain

```mermaid
sequenceDiagram
    participant Request
    participant AuthFilter
    participant Authenticator
    participant Context
    participant NextHandler
    
    Request->>AuthFilter: HTTP Request
    AuthFilter->>Authenticator: Authenticate
    Authenticator-->>AuthFilter: User Info
    AuthFilter->>Context: Add User
    AuthFilter->>NextHandler: Continue
```

### Server Configuration

```go
config := &server.Config{
    Authentication: server.AuthenticationInfo{
        Authenticator: authenticator,
        // ...
    },
}
```

## Best Practices

### 1. Multiple Authenticators

Use union authenticator for flexibility:
```go
authenticators := []authenticator.Request{
    x509Auth,
    oidcAuth,
    webhookAuth,
}
unionAuth := union.New(authenticators...)
```

### 2. Token Caching

Enable caching for performance:
```go
cachedAuth := cache.New(
    tokenAuth,
    true,  // cache success
    2*time.Minute,  // success TTL
    30*time.Second, // failure TTL
)
```

### 3. Audience Validation

Always validate token audiences:
```go
if !response.Audiences.Has(expectedAudience) {
    return nil, false, errors.New("invalid audience")
}
```

### 4. Error Handling

Distinguish between auth failures and errors:
```go
user, ok, err := authenticator.AuthenticateRequest(req)
if err != nil {
    // System error - log and return 500
}
if !ok {
    // Authentication failed - return 401
}
// Success - continue with user
```

## Security Considerations

### 1. Token Validation

- Verify signatures
- Check expiration
- Validate audiences
- Verify issuer

### 2. Certificate Validation

- Check certificate chain
- Verify not revoked
- Validate usage
- Check expiration

### 3. Credential Storage

- Never log tokens
- Use secure storage
- Rotate regularly
- Limit scope

### 4. Anonymous Access

- Disable if not needed
- Limit to public endpoints
- Monitor usage

## Testing

### Mock Authenticator

```go
type fakeAuthenticator struct {
    user user.Info
    ok   bool
    err  error
}

func (f *fakeAuthenticator) AuthenticateRequest(req *http.Request) (*authenticator.Response, bool, error) {
    if f.err != nil {
        return nil, false, f.err
    }
    if !f.ok {
        return nil, false, nil
    }
    return &authenticator.Response{User: f.user}, true, nil
}
```

### Testing Tokens

```go
// Create test token
token := createTestJWT(t, claims)

// Test authentication
response, ok, err := tokenAuth.AuthenticateToken(ctx, token)
assert.NoError(t, err)
assert.True(t, ok)
assert.Equal(t, "john", response.User.GetName())
```

## Related Packages

- **pkg/authorization**: Uses user info for authorization
- **pkg/audit**: Logs user info in audit events
- **pkg/server**: Integrates authentication into handler chain
- **pkg/endpoints/request**: Extracts user from context

## References

- [Kubernetes Authentication](https://kubernetes.io/docs/reference/access-authn-authz/authentication/)
- [Service Account Tokens](https://kubernetes.io/docs/reference/access-authn-authz/service-accounts-admin/)
- [OIDC Authentication](https://kubernetes.io/docs/reference/access-authn-authz/authentication/#openid-connect-tokens)
- [Webhook Token Authentication](https://kubernetes.io/docs/reference/access-authn-authz/authentication/#webhook-token-authentication)
