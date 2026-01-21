---
title: "Serialization"
weight: 5
---


## Overview

The `pkg/runtime/serializer` package provides multiple serialization formats for Kubernetes API objects. It supports JSON, YAML, Protocol Buffers, and CBOR, with automatic version conversion and content negotiation.

## Purpose

The serializer package provides:

1. **Multiple Formats**: JSON, YAML, Protobuf, CBOR
2. **Content Negotiation**: Select format based on HTTP headers
3. **Version Conversion**: Automatic conversion during serialization
4. **Streaming**: Efficient streaming for large collections
5. **Strict Mode**: Validate unknown fields
6. **Pretty Printing**: Human-readable output

## Architecture

![Diagram](/diagrams/diagram-e243627b.svg)

## CodecFactory

The central factory for creating codecs and serializers.

### Structure

```go
type CodecFactory struct {
    scheme           *runtime.Scheme
    universal        runtime.Decoder
    accepts          []runtime.SerializerInfo
    legacySerializer runtime.Serializer
}
```

### Creating a CodecFactory

```go
import (
    "k8s.io/apimachinery/pkg/runtime"
    "k8s.io/apimachinery/pkg/runtime/serializer"
)

// Create scheme
scheme := runtime.NewScheme()

// Register types
scheme.AddKnownTypes(schema.GroupVersion{Group: "apps", Version: "v1"},
    &Deployment{},
    &DeploymentList{},
)

// Create codec factory
codecFactory := serializer.NewCodecFactory(scheme)
```

### CodecFactory Options

```go
type CodecFactoryOptions struct {
    Strict  bool  // Enable strict decoding
    Pretty  bool  // Enable pretty printing
    
    StreamingCollectionsEncodingToJSON     bool
    StreamingCollectionsEncodingToProtobuf bool
}
```

**Option Mutators:**

```go
// Enable pretty printing
codecFactory := serializer.NewCodecFactory(scheme, serializer.EnablePretty)

// Enable strict mode
codecFactory := serializer.NewCodecFactory(scheme, serializer.EnableStrict)

// Multiple options
codecFactory := serializer.NewCodecFactory(scheme, 
    serializer.EnablePretty,
    serializer.EnableStrict,
)
```

### Getting Codecs

```go
// Universal deserializer (handles any registered format)
decoder := codecFactory.UniversalDeserializer()

// Encoder for specific version
encoder := codecFactory.EncoderForVersion(
    jsonSerializer,
    schema.GroupVersion{Group: "apps", Version: "v1"},
)

// Decoder for specific version
decoder := codecFactory.DecoderToVersion(
    jsonSerializer,
    schema.GroupVersion{Group: "apps", Version: "v1"},
)

// Legacy codec (for backward compatibility)
codec := codecFactory.LegacyCodec(
    schema.GroupVersion{Group: "apps", Version: "v1"},
)
```

## JSON Serializer

### Features

- **Standard JSON**: RFC 8259 compliant
- **Pretty Printing**: Human-readable formatting
- **Strict Mode**: Reject unknown fields
- **Streaming**: Efficient for large lists

### Creating JSON Serializer

```go
import "k8s.io/apimachinery/pkg/runtime/serializer/json"

jsonSerializer := json.NewSerializerWithOptions(
    json.DefaultMetaFactory,
    scheme,
    scheme,
    json.SerializerOptions{
        Yaml:   false,
        Pretty: false,
        Strict: false,
    },
)
```

### Encoding JSON

```go
var buf bytes.Buffer

// Encode to JSON
err := jsonSerializer.Encode(deployment, &buf)
if err != nil {
    return err
}

jsonData := buf.Bytes()
```

### Decoding JSON

```go
obj, gvk, err := jsonSerializer.Decode(jsonData, nil, nil)
if err != nil {
    return err
}

deployment := obj.(*appsv1.Deployment)
```

### Pretty Printing

```go
prettySerializer := json.NewSerializerWithOptions(
    json.DefaultMetaFactory,
    scheme,
    scheme,
    json.SerializerOptions{
        Yaml:   false,
        Pretty: true,  // Enable pretty printing
        Strict: false,
    },
)

// Produces formatted JSON
err := prettySerializer.Encode(deployment, os.Stdout)
```

### Strict Mode

```go
strictSerializer := json.NewSerializerWithOptions(
    json.DefaultMetaFactory,
    scheme,
    scheme,
    json.SerializerOptions{
        Yaml:   false,
        Pretty: false,
        Strict: true,  // Reject unknown fields
    },
)

// Will fail if JSON contains unknown fields
obj, _, err := strictSerializer.Decode(jsonData, nil, nil)
```

## YAML Serializer

### Features

- **YAML 1.2**: Standard YAML format
- **JSON Compatible**: Built on JSON serializer
- **Human Readable**: Easy to read and edit

### Creating YAML Serializer

```go
yamlSerializer := json.NewSerializerWithOptions(
    json.DefaultMetaFactory,
    scheme,
    scheme,
    json.SerializerOptions{
        Yaml:   true,  // Enable YAML mode
        Pretty: false,
        Strict: false,
    },
)
```

### Encoding YAML

```go
var buf bytes.Buffer
err := yamlSerializer.Encode(deployment, &buf)
if err != nil {
    return err
}

yamlData := buf.Bytes()
```

### Decoding YAML

```go
obj, gvk, err := yamlSerializer.Decode(yamlData, nil, nil)
if err != nil {
    return err
}

deployment := obj.(*appsv1.Deployment)
```

## Protocol Buffers Serializer

### Features

- **Binary Format**: Compact and efficient
- **Fast**: Faster than JSON
- **Streaming**: Efficient for large collections
- **Schema Evolution**: Backward compatible

### Creating Protobuf Serializer

```go
import "k8s.io/apimachinery/pkg/runtime/serializer/protobuf"

protoSerializer := protobuf.NewSerializer(scheme, scheme)
```

### Encoding Protobuf

```go
var buf bytes.Buffer
err := protoSerializer.Encode(deployment, &buf)
if err != nil {
    return err
}

protoData := buf.Bytes()
```

### Decoding Protobuf

```go
obj, gvk, err := protoSerializer.Decode(protoData, nil, nil)
if err != nil {
    return err
}

deployment := obj.(*appsv1.Deployment)
```

### Protobuf Framing

For streaming:

```go
// Length-delimited framing
framer := protobuf.LengthDelimitedFramer

// Create framed writer
framedWriter := framer.NewFrameWriter(writer)

// Encode with framing
err := protoSerializer.Encode(obj, framedWriter)
```

## CBOR Serializer

### Features

- **Concise Binary**: RFC 8949 compliant
- **Efficient**: Smaller than JSON
- **Streaming**: CBOR sequences (RFC 8742)
- **Modern**: Designed for IoT and constrained environments

### Creating CBOR Serializer

```go
import "k8s.io/apimachinery/pkg/runtime/serializer/cbor"

cborSerializer := cbor.NewSerializer(scheme, scheme)
```

### Content Types

```go
const (
    ContentTypeCBOR         = "application/cbor"
    ContentTypeCBORSequence = "application/cbor-seq"
)
```

## Versioning Codec

Wraps serializers to add version conversion.

### Structure

```go
type codec struct {
    encoder   runtime.Encoder
    decoder   runtime.Decoder
    convertor runtime.ObjectConvertor
    creater   runtime.ObjectCreater
    typer     runtime.ObjectTyper
    
    encodeVersion runtime.GroupVersioner
    decodeVersion runtime.GroupVersioner
}
```

### Creating Versioning Codec

```go
import "k8s.io/apimachinery/pkg/runtime/serializer/versioning"

versioningCodec := versioning.NewCodec(
    jsonSerializer,                                    // Base serializer
    jsonSerializer,                                    // Base deserializer
    scheme,                                            // Convertor
    scheme,                                            // Creater
    scheme,                                            // Typer
    schema.GroupVersion{Group: "apps", Version: "v1"}, // Encode version
    schema.GroupVersion{Group: "apps", Version: "v1"}, // Decode version
    "versioning-codec",                                // Identifier
)
```

### Version Conversion Flow

![Diagram](/diagrams/diagram-bb323d9e.svg)

## Streaming Serialization

### Features

- **Efficient**: Process large collections without loading all into memory
- **Framing**: Separate objects in stream
- **Watch**: Used for watch streams

### Streaming Interface

```go
type StreamSerializerInfo struct {
    EncodesAsText bool
    Serializer    runtime.Serializer
    Framer        runtime.Framer
}
```

### Framer Interface

```go
type Framer interface {
    NewFrameReader(r io.ReadCloser) io.ReadCloser
    NewFrameWriter(w io.Writer) io.Writer
}
```

### JSON Framing

```go
// JSON uses newline framing
var Framer = jsonFramer{}

type jsonFramer struct{}

func (jsonFramer) NewFrameWriter(w io.Writer) io.Writer {
    return &jsonFrameWriter{w: w}
}

func (jsonFramer) NewFrameReader(r io.ReadCloser) io.ReadCloser {
    return &jsonFrameReader{r: r}
}
```

### Protobuf Framing

```go
// Protobuf uses length-delimited framing
var LengthDelimitedFramer = lengthDelimitedFramer{}

type lengthDelimitedFramer struct{}

func (lengthDelimitedFramer) NewFrameWriter(w io.Writer) io.Writer {
    return &lengthDelimitedFrameWriter{w: w}
}
```

### Using Streaming

```go
// Create streaming encoder
streamInfo := codecFactory.SupportedMediaTypes()[0].StreamSerializer
framer := streamInfo.Framer
serializer := streamInfo.Serializer

// Create framed writer
framedWriter := framer.NewFrameWriter(writer)

// Encode multiple objects
for _, obj := range objects {
    err := serializer.Encode(obj, framedWriter)
    if err != nil {
        return err
    }
}
```

## Format Recognition

Automatically detect serialization format.

### Recognizer

```go
import "k8s.io/apimachinery/pkg/runtime/serializer/recognizer"

// Create recognizer with multiple decoders
decoder := recognizer.NewDecoder(
    jsonSerializer,
    yamlSerializer,
    protoSerializer,
)

// Automatically detects format
obj, gvk, err := decoder.Decode(data, nil, nil)
```

### Recognition Logic

```go
// JSON: starts with '{' or '['
// YAML: starts with '---' or has YAML-specific syntax
// Protobuf: binary data with protobuf magic bytes
// CBOR: starts with CBOR major type
```

## Content Negotiation

### Negotiated Codec

```go
type negotiatedSerializer struct {
    scheme       *runtime.Scheme
    serializers  []runtime.SerializerInfo
}
```

### Getting Serializer by Media Type

```go
// Get supported media types
mediaTypes := codecFactory.SupportedMediaTypes()

// Find serializer for media type
for _, info := range mediaTypes {
    if info.MediaType == "application/json" {
        serializer = info.Serializer
        break
    }
}
```

### HTTP Content Negotiation

```go
// Client specifies Accept header
Accept: application/json, application/yaml;q=0.9

// Server selects best match
func SelectSerializer(accept string, available []SerializerInfo) SerializerInfo {
    // Parse Accept header
    // Match against available serializers
    // Return best match
}
```

## Serialization Options

### JSON Options

```go
type SerializerOptions struct {
    Yaml   bool  // Output YAML instead of JSON
    Pretty bool  // Pretty print
    Strict bool  // Strict decoding
    
    StreamingCollectionsEncoding bool
}
```

### Protobuf Options

```go
type SerializerOptions struct {
    StreamingCollectionsEncoding bool
}
```

## Common Patterns

### 1. Universal Decode

```go
// Decode any supported format
decoder := codecFactory.UniversalDeserializer()
obj, gvk, err := decoder.Decode(data, nil, nil)
```

### 2. Encode to Specific Version

```go
// Encode internal object to v1
encoder := codecFactory.EncoderForVersion(
    jsonSerializer,
    schema.GroupVersion{Group: "apps", Version: "v1"},
)

var buf bytes.Buffer
err := encoder.Encode(internalDeployment, &buf)
```

### 3. Decode to Specific Version

```go
// Decode to internal version
decoder := codecFactory.DecoderToVersion(
    jsonSerializer,
    runtime.InternalGroupVersioner,
)

obj, gvk, err := decoder.Decode(data, nil, nil)
```

### 4. Round-Trip Conversion

```go
// Encode
var buf bytes.Buffer
err := encoder.Encode(obj, &buf)

// Decode
obj2, _, err := decoder.Decode(buf.Bytes(), nil, nil)

// obj and obj2 should be equal
```

### 5. Multi-Format Support

```go
func EncodeObject(obj runtime.Object, format string) ([]byte, error) {
    var serializer runtime.Serializer
    
    switch format {
    case "json":
        serializer = jsonSerializer
    case "yaml":
        serializer = yamlSerializer
    case "protobuf":
        serializer = protoSerializer
    default:
        return nil, fmt.Errorf("unsupported format: %s", format)
    }
    
    var buf bytes.Buffer
    err := serializer.Encode(obj, &buf)
    return buf.Bytes(), err
}
```

## Performance Considerations

### 1. Format Selection

| Format | Size | Speed | Human Readable |
|--------|------|-------|----------------|
| JSON | Medium | Medium | Yes |
| YAML | Large | Slow | Yes |
| Protobuf | Small | Fast | No |
| CBOR | Small | Fast | No |

### 2. Streaming vs Buffered

```go
// Buffered (loads all into memory)
var buf bytes.Buffer
for _, obj := range objects {
    encoder.Encode(obj, &buf)
}
data := buf.Bytes()

// Streaming (processes one at a time)
framedWriter := framer.NewFrameWriter(writer)
for _, obj := range objects {
    encoder.Encode(obj, framedWriter)
}
```

### 3. Caching

```go
// Cache encoded representations
type CachedObject struct {
    obj   runtime.Object
    cache map[runtime.Identifier][]byte
}

func (c *CachedObject) CacheEncode(id runtime.Identifier, encode func(runtime.Object, io.Writer) error, w io.Writer) error {
    if data, ok := c.cache[id]; ok {
        _, err := w.Write(data)
        return err
    }
    
    var buf bytes.Buffer
    if err := encode(c.obj, &buf); err != nil {
        return err
    }
    
    data := buf.Bytes()
    c.cache[id] = data
    _, err := w.Write(data)
    return err
}
```

## Testing Support

### Mock Serializer

```go
type FakeSerializer struct {
    EncodeFunc func(runtime.Object, io.Writer) error
    DecodeFunc func([]byte, *schema.GroupVersionKind, runtime.Object) (runtime.Object, *schema.GroupVersionKind, error)
}

func (f *FakeSerializer) Encode(obj runtime.Object, w io.Writer) error {
    return f.EncodeFunc(obj, w)
}

func (f *FakeSerializer) Decode(data []byte, defaults *schema.GroupVersionKind, into runtime.Object) (runtime.Object, *schema.GroupVersionKind, error) {
    return f.DecodeFunc(data, defaults, into)
}
```

## Summary

The serialization package provides:

1. **Multiple Formats**: JSON, YAML, Protobuf, CBOR
2. **CodecFactory**: Central factory for creating codecs
3. **Version Conversion**: Automatic conversion during serialization
4. **Streaming**: Efficient streaming for large collections
5. **Content Negotiation**: Select format based on HTTP headers
6. **Strict Mode**: Validate unknown fields
7. **Pretty Printing**: Human-readable output
8. **Format Recognition**: Automatic format detection

This package enables Kubernetes to support multiple serialization formats while maintaining backward compatibility and providing efficient serialization for different use cases.

