---
title: "Watch Package"
weight: 4
---


## Overview

The `pkg/watch` package provides interfaces and implementations for watching changes to Kubernetes resources in real-time. It enables clients to receive notifications when resources are added, modified, or deleted, without polling.

## Purpose

The watch package provides:

1. **Watch Interface**: Core interface for observing resource changes
2. **Event Types**: Typed events for different change types
3. **Stream Watching**: Watch resources from streaming connections
4. **Broadcasting**: Distribute events to multiple watchers
5. **Filtering**: Filter events based on criteria
6. **Multiplexing**: Combine multiple watch sources

## Architecture

![Diagram](/diagrams/diagram-9ccb8748.svg)

## Core Interface

### Watch Interface

The fundamental interface for watching resources:

```go
type Interface interface {
    // Stop tells the producer to stop sending events
    // Consumer should keep watching for events until the channel is closed
    Stop()
    
    // ResultChan returns a channel which will receive events
    // Producer must close this channel when stopping
    ResultChan() <-chan Event
}
```

**Usage Pattern:**

```go
watcher, err := client.Watch(ctx, options)
if err != nil {
    return err
}
defer watcher.Stop()

for event := range watcher.ResultChan() {
    // Process event
}
```

### Event Type

Represents a single change event:

```go
type Event struct {
    Type   EventType
    Object runtime.Object
}
```

### Event Types

```go
type EventType string

const (
    Added    EventType = "ADDED"
    Modified EventType = "MODIFIED"
    Deleted  EventType = "DELETED"
    Bookmark EventType = "BOOKMARK"
    Error    EventType = "ERROR"
)
```

**Event Type Semantics:**

![Diagram](/diagrams/diagram-3917700b.svg)

1. **ADDED**: A new resource was created
   - Object contains the new resource state

2. **MODIFIED**: An existing resource was updated
   - Object contains the updated resource state

3. **DELETED**: A resource was removed
   - Object contains the final state before deletion

4. **BOOKMARK**: Synchronization point marker
   - Used for resuming watches from a known point
   - Object contains only ResourceVersion
   - Guarantees no events were missed up to this point

5. **ERROR**: An error occurred in the watch
   - Object is typically a Status object with error details
   - Watch should be restarted

## StreamWatcher

Watches a stream and converts it to watch events.

### Structure

```go
type StreamWatcher struct {
    source   Decoder
    reporter Reporter
    result   chan Event
    done     chan struct{}
}
```

### Decoder Interface

Decodes events from a stream:

```go
type Decoder interface {
    // Decode returns the event type and object
    // Blocks until data is available or error occurs
    Decode() (action EventType, object runtime.Object, err error)
    
    // Close the underlying stream
    Close()
}
```

### Reporter Interface

Converts errors to watch events:

```go
type Reporter interface {
    // AsObject converts an error to a runtime.Object
    AsObject(err error) runtime.Object
}
```

### Creating a StreamWatcher

```go
// Create decoder for the stream
decoder := json.NewDecoder(stream)

// Create reporter
reporter := &errorReporter{}

// Create stream watcher
watcher := watch.NewStreamWatcher(decoder, reporter)

// Use the watcher
for event := range watcher.ResultChan() {
    switch event.Type {
    case watch.Added:
        fmt.Println("Added:", event.Object)
    case watch.Modified:
        fmt.Println("Modified:", event.Object)
    case watch.Deleted:
        fmt.Println("Deleted:", event.Object)
    case watch.Error:
        fmt.Println("Error:", event.Object)
    }
}
```

## Broadcaster

Distributes events to multiple watchers.

### Structure

```go
type Broadcaster struct {
    watchers            map[int64]*broadcasterWatcher
    incoming            chan Event
    watchQueueLength    int
    fullChannelBehavior FullChannelBehavior
}
```

### Full Channel Behavior

```go
type FullChannelBehavior int

const (
    WaitIfChannelFull FullChannelBehavior = iota
    DropIfChannelFull
)
```

- **WaitIfChannelFull**: Block until watcher can receive (default)
- **DropIfChannelFull**: Skip slow watchers, continue with others

### Creating a Broadcaster

```go
// Create broadcaster with queue length and behavior
broadcaster := watch.NewBroadcaster(100, watch.WaitIfChannelFull)

// Start watching
watcher1 := broadcaster.Watch()
watcher2 := broadcaster.Watch()

// Send events to all watchers
broadcaster.Action(watch.Added, pod)
broadcaster.Action(watch.Modified, pod)
broadcaster.Action(watch.Deleted, pod)

// Shutdown
broadcaster.Shutdown()
```

### Broadcasting Pattern

![Diagram](/diagrams/diagram-5d574d85.svg)

### Methods

```go
// Watch creates a new watcher
func (b *Broadcaster) Watch() Interface

// WatchWithPrefix creates a watcher with a filter function
func (b *Broadcaster) WatchWithPrefix(filter FilterFunc) Interface

// Action sends an event to all watchers
func (b *Broadcaster) Action(action EventType, obj runtime.Object)

// Shutdown stops the broadcaster and closes all watchers
func (b *Broadcaster) Shutdown()
```

## Mux (Multiplexer)

Combines multiple watch sources into a single watch interface.

### Structure

```go
type Mux struct {
    lock        sync.RWMutex
    watchers    map[int64]*muxWatcher
    broadcaster *Broadcaster
}
```

### Creating a Mux

```go
// Create mux
mux := watch.NewMux(100)

// Add watch sources
mux.AddSource(watcher1)
mux.AddSource(watcher2)
mux.AddSource(watcher3)

// Watch combined stream
combinedWatcher := mux.Watch()

for event := range combinedWatcher.ResultChan() {
    // Receives events from all sources
}
```

### Use Cases

1. **Multiple API Servers**: Watch resources from multiple clusters
2. **Aggregation**: Combine watches for different resource types
3. **Failover**: Switch between primary and backup sources

## Filter

Filters watch events based on criteria.

### Creating a Filter

```go
// Create base watcher
baseWatcher, _ := client.Watch(ctx, options)

// Create filter function
filterFunc := func(event watch.Event) (watch.Event, bool) {
    pod := event.Object.(*v1.Pod)
    
    // Only pass through running pods
    if pod.Status.Phase == v1.PodRunning {
        return event, true
    }
    
    return watch.Event{}, false
}

// Create filtered watcher
filteredWatcher := watch.Filter(baseWatcher, filterFunc)

// Use filtered watcher
for event := range filteredWatcher.ResultChan() {
    // Only receives events for running pods
}
```

### Filter Function

```go
type FilterFunc func(in Event) (out Event, keep bool)
```

**Parameters:**
- `in`: Input event
- Returns:
  - `out`: Potentially modified event
  - `keep`: Whether to pass the event through

## Watch Patterns

### 1. Basic Watch

```go
watcher, err := clientset.CoreV1().Pods("default").Watch(ctx, metav1.ListOptions{})
if err != nil {
    return err
}
defer watcher.Stop()

for event := range watcher.ResultChan() {
    pod := event.Object.(*v1.Pod)
    
    switch event.Type {
    case watch.Added:
        fmt.Printf("Pod added: %s\n", pod.Name)
    case watch.Modified:
        fmt.Printf("Pod modified: %s\n", pod.Name)
    case watch.Deleted:
        fmt.Printf("Pod deleted: %s\n", pod.Name)
    case watch.Error:
        status := event.Object.(*metav1.Status)
        fmt.Printf("Watch error: %s\n", status.Message)
        return fmt.Errorf("watch error")
    }
}
```

### 2. Watch with Timeout

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
defer cancel()

watcher, err := clientset.CoreV1().Pods("default").Watch(ctx, metav1.ListOptions{})
if err != nil {
    return err
}
defer watcher.Stop()

for {
    select {
    case event, ok := <-watcher.ResultChan():
        if !ok {
            return nil  // Channel closed
        }
        // Process event
        
    case <-ctx.Done():
        return ctx.Err()  // Timeout
    }
}
```

### 3. Watch with Restart

```go
func WatchWithRestart(ctx context.Context, client kubernetes.Interface) error {
    resourceVersion := ""
    
    for {
        watcher, err := client.CoreV1().Pods("default").Watch(ctx, metav1.ListOptions{
            ResourceVersion: resourceVersion,
        })
        if err != nil {
            return err
        }
        
        for event := range watcher.ResultChan() {
            switch event.Type {
            case watch.Error:
                watcher.Stop()
                time.Sleep(time.Second)
                continue  // Restart watch
                
            case watch.Bookmark:
                // Update resource version for restart
                pod := event.Object.(*v1.Pod)
                resourceVersion = pod.ResourceVersion
                
            default:
                // Process event
                pod := event.Object.(*v1.Pod)
                resourceVersion = pod.ResourceVersion
            }
        }
        
        // Restart watch
        time.Sleep(time.Second)
    }
}
```

### 4. Filtered Watch

```go
watcher, err := clientset.CoreV1().Pods("default").Watch(ctx, metav1.ListOptions{
    LabelSelector: "app=nginx",
    FieldSelector: "status.phase=Running",
})
```

### 5. Watch All Namespaces

```go
watcher, err := clientset.CoreV1().Pods(metav1.NamespaceAll).Watch(ctx, metav1.ListOptions{})
```

## Resource Version and Bookmarks

### Resource Version

Every Kubernetes object has a ResourceVersion:

```go
type ObjectMeta struct {
    ResourceVersion string
    // ...
}
```

**Purpose:**
- Identifies a specific version of an object
- Used to resume watches from a known point
- Prevents missing events during reconnection

### Using Resource Version

```go
// List to get current resource version
list, err := clientset.CoreV1().Pods("default").List(ctx, metav1.ListOptions{})
resourceVersion := list.ResourceVersion

// Watch from that point forward
watcher, err := clientset.CoreV1().Pods("default").Watch(ctx, metav1.ListOptions{
    ResourceVersion: resourceVersion,
})
```

### Bookmark Events

```go
for event := range watcher.ResultChan() {
    switch event.Type {
    case watch.Bookmark:
        // Update resource version for restart
        accessor, _ := meta.Accessor(event.Object)
        resourceVersion := accessor.GetResourceVersion()
        
        // Save for later restart
        saveResourceVersion(resourceVersion)
    }
}
```

## Error Handling

### Watch Errors

```go
for event := range watcher.ResultChan() {
    if event.Type == watch.Error {
        status := event.Object.(*metav1.Status)
        
        switch status.Code {
        case http.StatusGone:
            // Resource version too old, restart from beginning
            resourceVersion = ""
            
        case http.StatusInternalServerError:
            // Server error, retry with backoff
            time.Sleep(time.Second)
            
        default:
            return fmt.Errorf("watch error: %s", status.Message)
        }
    }
}
```

### Connection Errors

```go
func WatchWithRetry(ctx context.Context) error {
    backoff := time.Second
    maxBackoff := time.Minute
    
    for {
        watcher, err := startWatch(ctx)
        if err != nil {
            time.Sleep(backoff)
            backoff = min(backoff*2, maxBackoff)
            continue
        }
        
        err = processWatch(watcher)
        if err != nil {
            time.Sleep(backoff)
            backoff = min(backoff*2, maxBackoff)
            continue
        }
        
        // Success, reset backoff
        backoff = time.Second
    }
}
```

## Performance Considerations

### 1. Channel Buffering

```go
// Default channel size
var DefaultChanSize int32 = 100

// Create watcher with custom buffer
watcher := watch.NewFake()
watcher.ResultChan() // Returns buffered channel
```

### 2. Slow Consumer Protection

```go
// Use DropIfChannelFull to prevent slow consumers from blocking
broadcaster := watch.NewBroadcaster(100, watch.DropIfChannelFull)
```

### 3. Resource Version Caching

```go
type WatchCache struct {
    resourceVersion string
    mu              sync.RWMutex
}

func (c *WatchCache) Update(rv string) {
    c.mu.Lock()
    c.resourceVersion = rv
    c.mu.Unlock()
}

func (c *WatchCache) Get() string {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.resourceVersion
}
```

## Testing Support

### Fake Watcher

```go
type FakeWatcher struct {
    result  chan Event
    stopped bool
}

func NewFake() *FakeWatcher {
    return &FakeWatcher{
        result: make(chan Event),
    }
}

func (f *FakeWatcher) Add(obj runtime.Object) {
    f.result <- Event{Type: Added, Object: obj}
}

func (f *FakeWatcher) Modify(obj runtime.Object) {
    f.result <- Event{Type: Modified, Object: obj}
}

func (f *FakeWatcher) Delete(obj runtime.Object) {
    f.result <- Event{Type: Deleted, Object: obj}
}

func (f *FakeWatcher) Error(obj runtime.Object) {
    f.result <- Event{Type: Error, Object: obj}
}
```

### Testing Pattern

```go
func TestWatcher(t *testing.T) {
    watcher := watch.NewFake()
    
    go func() {
        watcher.Add(pod1)
        watcher.Modify(pod2)
        watcher.Delete(pod3)
        watcher.Stop()
    }()
    
    events := []watch.Event{}
    for event := range watcher.ResultChan() {
        events = append(events, event)
    }
    
    assert.Len(t, events, 3)
    assert.Equal(t, watch.Added, events[0].Type)
    assert.Equal(t, watch.Modified, events[1].Type)
    assert.Equal(t, watch.Deleted, events[2].Type)
}
```

## Integration with Informers

The watch package is the foundation for informers (from client-go):

![Diagram](/diagrams/diagram-74f3d054.svg)

## Summary

The watch package provides:

1. **Watch Interface**: Standard interface for observing changes
2. **Event Types**: Typed events (Added, Modified, Deleted, Bookmark, Error)
3. **StreamWatcher**: Watch resources from streaming connections
4. **Broadcaster**: Distribute events to multiple watchers
5. **Mux**: Combine multiple watch sources
6. **Filter**: Filter events based on criteria
7. **Resource Version**: Resume watches from known points
8. **Error Handling**: Robust error handling and retry mechanisms

This package is fundamental to Kubernetes' real-time update model, enabling efficient resource monitoring without polling.

