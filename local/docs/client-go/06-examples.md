# Examples and Patterns

This document provides practical examples and common patterns for using `client-go`.

## Table of Contents

1. [Basic Client Operations](#basic-client-operations)
2. [Controller Patterns](#controller-patterns)
3. [Custom Resource Definitions](#custom-resource-definitions)
4. [Server-Side Apply](#server-side-apply)
5. [Leader Election](#leader-election)
6. [Advanced Patterns](#advanced-patterns)

## Basic Client Operations

### Example 1: Simple Pod Operations

```go
package main

import (
    "context"
    "fmt"
    "log"
    
    corev1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
)

func main() {
    // Create config
    config, err := rest.InClusterConfig()
    if err != nil {
        log.Fatal(err)
    }
    
    // Create clientset
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        log.Fatal(err)
    }
    
    ctx := context.Background()
    
    // Create a pod
    pod := &corev1.Pod{
        ObjectMeta: metav1.ObjectMeta{
            Name: "example-pod",
            Labels: map[string]string{
                "app": "example",
            },
        },
        Spec: corev1.PodSpec{
            Containers: []corev1.Container{
                {
                    Name:  "nginx",
                    Image: "nginx:1.21",
                    Ports: []corev1.ContainerPort{
                        {
                            ContainerPort: 80,
                        },
                    },
                },
            },
        },
    }
    
    createdPod, err := clientset.CoreV1().Pods("default").Create(ctx, pod, metav1.CreateOptions{})
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Created pod: %s\n", createdPod.Name)
    
    // Get the pod
    retrievedPod, err := clientset.CoreV1().Pods("default").Get(ctx, "example-pod", metav1.GetOptions{})
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Retrieved pod: %s, Status: %s\n", retrievedPod.Name, retrievedPod.Status.Phase)
    
    // List pods with label selector
    podList, err := clientset.CoreV1().Pods("default").List(ctx, metav1.ListOptions{
        LabelSelector: "app=example",
    })
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Found %d pods\n", len(podList.Items))
    
    // Update the pod
    retrievedPod.Labels["environment"] = "production"
    updatedPod, err := clientset.CoreV1().Pods("default").Update(ctx, retrievedPod, metav1.UpdateOptions{})
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Updated pod: %s\n", updatedPod.Name)
    
    // Delete the pod
    err = clientset.CoreV1().Pods("default").Delete(ctx, "example-pod", metav1.DeleteOptions{})
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println("Deleted pod")
}
```

### Example 2: Watching Resources

```go
package main

import (
    "context"
    "fmt"
    "log"
    
    corev1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/watch"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
)

func main() {
    config, err := rest.InClusterConfig()
    if err != nil {
        log.Fatal(err)
    }
    
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        log.Fatal(err)
    }
    
    ctx := context.Background()
    
    // Start watching pods
    watcher, err := clientset.CoreV1().Pods("default").Watch(ctx, metav1.ListOptions{
        LabelSelector: "app=example",
    })
    if err != nil {
        log.Fatal(err)
    }
    defer watcher.Stop()
    
    fmt.Println("Watching for pod changes...")
    
    for event := range watcher.ResultChan() {
        pod, ok := event.Object.(*corev1.Pod)
        if !ok {
            continue
        }
        
        switch event.Type {
        case watch.Added:
            fmt.Printf("Pod ADDED: %s\n", pod.Name)
        case watch.Modified:
            fmt.Printf("Pod MODIFIED: %s, Phase: %s\n", pod.Name, pod.Status.Phase)
        case watch.Deleted:
            fmt.Printf("Pod DELETED: %s\n", pod.Name)
        case watch.Error:
            fmt.Printf("Watch ERROR: %v\n", event.Object)
        }
    }
}
```

## Controller Patterns

### Example 3: Basic Controller with Informer

```go
package main

import (
    "context"
    "fmt"
    "log"
    "time"
    
    corev1 "k8s.io/api/core/v1"
    utilruntime "k8s.io/apimachinery/pkg/util/runtime"
    "k8s.io/apimachinery/pkg/util/wait"
    "k8s.io/client-go/informers"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
    "k8s.io/client-go/tools/cache"
    "k8s.io/client-go/util/workqueue"
)

type Controller struct {
    clientset kubernetes.Interface
    podLister cache.GenericLister
    podSynced cache.InformerSynced
    workqueue workqueue.RateLimitingInterface
}

func NewController(clientset kubernetes.Interface, informerFactory informers.SharedInformerFactory) *Controller {
    podInformer := informerFactory.Core().V1().Pods()
    
    controller := &Controller{
        clientset: clientset,
        podLister: podInformer.Lister(),
        podSynced: podInformer.Informer().HasSynced,
        workqueue: workqueue.NewRateLimitingQueue(workqueue.DefaultControllerRateLimiter()),
    }
    
    // Add event handlers
    podInformer.Informer().AddEventHandler(cache.ResourceEventHandlerFuncs{
        AddFunc: controller.enqueuePod,
        UpdateFunc: func(old, new interface{}) {
            controller.enqueuePod(new)
        },
        DeleteFunc: controller.enqueuePod,
    })
    
    return controller
}

func (c *Controller) enqueuePod(obj interface{}) {
    key, err := cache.MetaNamespaceKeyFunc(obj)
    if err != nil {
        utilruntime.HandleError(err)
        return
    }
    c.workqueue.Add(key)
}

func (c *Controller) Run(workers int, stopCh <-chan struct{}) error {
    defer utilruntime.HandleCrash()
    defer c.workqueue.ShutDown()
    
    log.Println("Starting controller")
    
    // Wait for cache sync
    log.Println("Waiting for informer caches to sync")
    if !cache.WaitForCacheSync(stopCh, c.podSynced) {
        return fmt.Errorf("failed to wait for caches to sync")
    }
    
    log.Println("Starting workers")
    for i := 0; i < workers; i++ {
        go wait.Until(c.runWorker, time.Second, stopCh)
    }
    
    log.Println("Started workers")
    <-stopCh
    log.Println("Shutting down workers")
    
    return nil
}

func (c *Controller) runWorker() {
    for c.processNextWorkItem() {
    }
}

func (c *Controller) processNextWorkItem() bool {
    obj, shutdown := c.workqueue.Get()
    if shutdown {
        return false
    }
    
    err := func(obj interface{}) error {
        defer c.workqueue.Done(obj)
        
        key, ok := obj.(string)
        if !ok {
            c.workqueue.Forget(obj)
            utilruntime.HandleError(fmt.Errorf("expected string in workqueue but got %#v", obj))
            return nil
        }
        
        if err := c.syncHandler(key); err != nil {
            c.workqueue.AddRateLimited(key)
            return fmt.Errorf("error syncing '%s': %s, requeuing", key, err.Error())
        }
        
        c.workqueue.Forget(obj)
        log.Printf("Successfully synced '%s'", key)
        return nil
    }(obj)
    
    if err != nil {
        utilruntime.HandleError(err)
    }
    
    return true
}

func (c *Controller) syncHandler(key string) error {
    namespace, name, err := cache.SplitMetaNamespaceKey(key)
    if err != nil {
        utilruntime.HandleError(fmt.Errorf("invalid resource key: %s", key))
        return nil
    }
    
    // Get pod from cache
    pod, err := c.podLister.ByNamespace(namespace).Get(name)
    if err != nil {
        if cache.IsNotFound(err) {
            log.Printf("Pod %s/%s no longer exists", namespace, name)
            return nil
        }
        return err
    }
    
    // Your reconciliation logic here
    log.Printf("Processing pod: %s/%s, Phase: %s", 
        pod.(*corev1.Pod).Namespace, 
        pod.(*corev1.Pod).Name, 
        pod.(*corev1.Pod).Status.Phase)
    
    return nil
}

func main() {
    config, err := rest.InClusterConfig()
    if err != nil {
        log.Fatal(err)
    }
    
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        log.Fatal(err)
    }
    
    // Create informer factory
    informerFactory := informers.NewSharedInformerFactory(clientset, time.Minute)
    
    // Create controller
    controller := NewController(clientset, informerFactory)
    
    // Start informers
    stopCh := make(chan struct{})
    defer close(stopCh)
    
    informerFactory.Start(stopCh)
    
    // Run controller
    if err := controller.Run(2, stopCh); err != nil {
        log.Fatalf("Error running controller: %s", err.Error())
    }
}
```

## Custom Resource Definitions

### Example 4: Working with CRDs using Dynamic Client

```go
package main

import (
    "context"
    "fmt"
    "log"
    
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
    "k8s.io/apimachinery/pkg/runtime/schema"
    "k8s.io/client-go/dynamic"
    "k8s.io/client-go/rest"
)

func main() {
    config, err := rest.InClusterConfig()
    if err != nil {
        log.Fatal(err)
    }
    
    // Create dynamic client
    dynamicClient, err := dynamic.NewForConfig(config)
    if err != nil {
        log.Fatal(err)
    }
    
    ctx := context.Background()
    
    // Define custom resource GVR
    gvr := schema.GroupVersionResource{
        Group:    "example.com",
        Version:  "v1",
        Resource: "myresources",
    }
    
    // Create custom resource
    myResource := &unstructured.Unstructured{
        Object: map[string]interface{}{
            "apiVersion": "example.com/v1",
            "kind":       "MyResource",
            "metadata": map[string]interface{}{
                "name": "my-custom-resource",
            },
            "spec": map[string]interface{}{
                "field1": "value1",
                "field2": 42,
                "nested": map[string]interface{}{
                    "key": "value",
                },
            },
        },
    }
    
    // Create the resource
    created, err := dynamicClient.Resource(gvr).Namespace("default").
        Create(ctx, myResource, metav1.CreateOptions{})
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Created resource: %s\n", created.GetName())
    
    // Get the resource
    retrieved, err := dynamicClient.Resource(gvr).Namespace("default").
        Get(ctx, "my-custom-resource", metav1.GetOptions{})
    if err != nil {
        log.Fatal(err)
    }
    
    // Access nested fields
    field1, found, err := unstructured.NestedString(retrieved.Object, "spec", "field1")
    if err != nil || !found {
        log.Fatal("field1 not found")
    }
    fmt.Printf("field1: %s\n", field1)
    
    field2, found, err := unstructured.NestedInt64(retrieved.Object, "spec", "field2")
    if err != nil || !found {
        log.Fatal("field2 not found")
    }
    fmt.Printf("field2: %d\n", field2)
    
    // Update the resource
    err = unstructured.SetNestedField(retrieved.Object, "updated-value", "spec", "field1")
    if err != nil {
        log.Fatal(err)
    }
    
    updated, err := dynamicClient.Resource(gvr).Namespace("default").
        Update(ctx, retrieved, metav1.UpdateOptions{})
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Updated resource: %s\n", updated.GetName())
    
    // List resources
    list, err := dynamicClient.Resource(gvr).Namespace("default").
        List(ctx, metav1.ListOptions{})
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Found %d resources\n", len(list.Items))
    
    // Delete the resource
    err = dynamicClient.Resource(gvr).Namespace("default").
        Delete(ctx, "my-custom-resource", metav1.DeleteOptions{})
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println("Deleted resource")
}
```

## Server-Side Apply

### Example 5: Using Server-Side Apply

```go
package main

import (
    "context"
    "fmt"
    "log"
    
    appsv1 "k8s.io/api/apps/v1"
    corev1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
    appsv1ac "k8s.io/client-go/applyconfigurations/apps/v1"
    corev1ac "k8s.io/client-go/applyconfigurations/core/v1"
    metav1ac "k8s.io/client-go/applyconfigurations/meta/v1"
    "k8s.io/utils/ptr"
)

func main() {
    config, err := rest.InClusterConfig()
    if err != nil {
        log.Fatal(err)
    }
    
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        log.Fatal(err)
    }
    
    ctx := context.Background()
    
    // Create deployment using Server-Side Apply
    deployment := appsv1ac.Deployment("nginx-deployment", "default").
        WithLabels(map[string]string{
            "app": "nginx",
        }).
        WithSpec(appsv1ac.DeploymentSpec().
            WithReplicas(3).
            WithSelector(metav1ac.LabelSelector().
                WithMatchLabels(map[string]string{
                    "app": "nginx",
                }),
            ).
            WithTemplate(corev1ac.PodTemplateSpec().
                WithLabels(map[string]string{
                    "app": "nginx",
                }).
                WithSpec(corev1ac.PodSpec().
                    WithContainers(
                        corev1ac.Container().
                            WithName("nginx").
                            WithImage("nginx:1.21").
                            WithPorts(corev1ac.ContainerPort().
                                WithContainerPort(80),
                            ),
                    ),
                ),
            ),
        )
    
    // Apply the deployment
    result, err := clientset.AppsV1().Deployments("default").
        Apply(ctx, deployment, metav1.ApplyOptions{
            FieldManager: "my-controller",
            Force:        false,
        })
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Applied deployment: %s\n", result.Name)
    
    // Later, update only replicas (partial apply)
    replicasOnly := appsv1ac.Deployment("nginx-deployment", "default").
        WithSpec(appsv1ac.DeploymentSpec().
            WithReplicas(5),
        )
    
    result, err = clientset.AppsV1().Deployments("default").
        Apply(ctx, replicasOnly, metav1.ApplyOptions{
            FieldManager: "my-controller",
        })
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Updated replicas to: %d\n", *result.Spec.Replicas)
    
    // Extract/Modify/Apply pattern
    existingDeployment, err := clientset.AppsV1().Deployments("default").
        Get(ctx, "nginx-deployment", metav1.GetOptions{})
    if err != nil {
        log.Fatal(err)
    }
    
    // Extract apply configuration
    deploymentApplyConfig, err := appsv1ac.ExtractDeployment(existingDeployment, "my-controller")
    if err != nil {
        log.Fatal(err)
    }
    
    // Modify
    deploymentApplyConfig.Spec.Template.Spec.WithContainers(
        corev1ac.Container().
            WithName("nginx").
            WithImage("nginx:1.22"),  // Update image
    )
    
    // Apply
    result, err = clientset.AppsV1().Deployments("default").
        Apply(ctx, deploymentApplyConfig, metav1.ApplyOptions{
            FieldManager: "my-controller",
        })
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Updated image in deployment: %s\n", result.Name)
}
```

## Leader Election

### Example 6: Controller with Leader Election

```go
package main

import (
    "context"
    "fmt"
    "log"
    "os"
    "time"
    
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
    "k8s.io/client-go/tools/leaderelection"
    "k8s.io/client-go/tools/leaderelection/resourcelock"
)

func main() {
    config, err := rest.InClusterConfig()
    if err != nil {
        log.Fatal(err)
    }
    
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        log.Fatal(err)
    }
    
    // Get pod name as identity
    podName := os.Getenv("POD_NAME")
    if podName == "" {
        podName = "unknown"
    }
    
    // Create resource lock
    lock := &resourcelock.LeaseLock{
        LeaseMeta: metav1.ObjectMeta{
            Name:      "my-controller-lock",
            Namespace: "kube-system",
        },
        Client: clientset.CoordinationV1(),
        LockConfig: resourcelock.ResourceLockConfig{
            Identity: podName,
        },
    }
    
    // Configure leader election
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()
    
    leaderelection.RunOrDie(ctx, leaderelection.LeaderElectionConfig{
        Lock:          lock,
        LeaseDuration: 15 * time.Second,
        RenewDeadline: 10 * time.Second,
        RetryPeriod:   2 * time.Second,
        Callbacks: leaderelection.LeaderCallbacks{
            OnStartedLeading: func(ctx context.Context) {
                log.Printf("%s: started leading", podName)
                runController(ctx, clientset)
            },
            OnStoppedLeading: func() {
                log.Printf("%s: stopped leading", podName)
                os.Exit(0)
            },
            OnNewLeader: func(identity string) {
                if identity == podName {
                    return
                }
                log.Printf("New leader elected: %s", identity)
            },
        },
        ReleaseOnCancel: true,
    })
}

func runController(ctx context.Context, clientset kubernetes.Interface) {
    log.Println("Running controller as leader")
    
    // Your controller logic here
    ticker := time.NewTicker(10 * time.Second)
    defer ticker.Stop()
    
    for {
        select {
        case <-ctx.Done():
            log.Println("Context cancelled, stopping controller")
            return
        case <-ticker.C:
            log.Println("Controller tick")
            // Do work
        }
    }
}
```

## Advanced Patterns

### Example 7: Multi-Resource Controller with Ownership

```go
package main

import (
    "context"
    "fmt"
    "log"
    
    appsv1 "k8s.io/api/apps/v1"
    corev1 "k8s.io/api/core/v1"
    "k8s.io/apimachinery/pkg/api/errors"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
    "k8s.io/utils/ptr"
)

// ReconcileDeploymentWithService creates a deployment and its associated service
func ReconcileDeploymentWithService(ctx context.Context, clientset kubernetes.Interface, name, namespace string) error {
    // Create or update deployment
    deployment := &appsv1.Deployment{
        ObjectMeta: metav1.ObjectMeta{
            Name:      name,
            Namespace: namespace,
            Labels: map[string]string{
                "app": name,
            },
        },
        Spec: appsv1.DeploymentSpec{
            Replicas: ptr.To[int32](3),
            Selector: &metav1.LabelSelector{
                MatchLabels: map[string]string{
                    "app": name,
                },
            },
            Template: corev1.PodTemplateSpec{
                ObjectMeta: metav1.ObjectMeta{
                    Labels: map[string]string{
                        "app": name,
                    },
                },
                Spec: corev1.PodSpec{
                    Containers: []corev1.Container{
                        {
                            Name:  "app",
                            Image: "nginx:1.21",
                            Ports: []corev1.ContainerPort{
                                {
                                    ContainerPort: 80,
                                    Name:          "http",
                                },
                            },
                        },
                    },
                },
            },
        },
    }
    
    // Create deployment
    createdDeployment, err := clientset.AppsV1().Deployments(namespace).Create(ctx, deployment, metav1.CreateOptions{})
    if err != nil {
        if errors.IsAlreadyExists(err) {
            // Update existing deployment
            createdDeployment, err = clientset.AppsV1().Deployments(namespace).Update(ctx, deployment, metav1.UpdateOptions{})
            if err != nil {
                return fmt.Errorf("failed to update deployment: %w", err)
            }
        } else {
            return fmt.Errorf("failed to create deployment: %w", err)
        }
    }
    
    // Create service with owner reference to deployment
    service := &corev1.Service{
        ObjectMeta: metav1.ObjectMeta{
            Name:      name,
            Namespace: namespace,
            Labels: map[string]string{
                "app": name,
            },
            OwnerReferences: []metav1.OwnerReference{
                *metav1.NewControllerRef(createdDeployment, appsv1.SchemeGroupVersion.WithKind("Deployment")),
            },
        },
        Spec: corev1.ServiceSpec{
            Selector: map[string]string{
                "app": name,
            },
            Ports: []corev1.ServicePort{
                {
                    Name:     "http",
                    Port:     80,
                    Protocol: corev1.ProtocolTCP,
                },
            },
            Type: corev1.ServiceTypeClusterIP,
        },
    }
    
    // Create service
    _, err = clientset.CoreV1().Services(namespace).Create(ctx, service, metav1.CreateOptions{})
    if err != nil {
        if errors.IsAlreadyExists(err) {
            // Update existing service
            _, err = clientset.CoreV1().Services(namespace).Update(ctx, service, metav1.UpdateOptions{})
            if err != nil {
                return fmt.Errorf("failed to update service: %w", err)
            }
        } else {
            return fmt.Errorf("failed to create service: %w", err)
        }
    }
    
    log.Printf("Successfully reconciled deployment and service: %s/%s", namespace, name)
    return nil
}

func main() {
    config, err := rest.InClusterConfig()
    if err != nil {
        log.Fatal(err)
    }
    
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        log.Fatal(err)
    }
    
    ctx := context.Background()
    
    err = ReconcileDeploymentWithService(ctx, clientset, "my-app", "default")
    if err != nil {
        log.Fatal(err)
    }
}
```

### Example 8: Finalizer Pattern

```go
package main

import (
    "context"
    "fmt"
    "log"
    "time"
    
    corev1 "k8s.io/api/core/v1"
    "k8s.io/apimachinery/pkg/api/errors"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
    "k8s.io/client-go/util/retry"
)

const finalizerName = "example.com/my-finalizer"

func addFinalizer(ctx context.Context, clientset kubernetes.Interface, namespace, name string) error {
    return retry.RetryOnConflict(retry.DefaultRetry, func() error {
        // Get latest version
        pod, err := clientset.CoreV1().Pods(namespace).Get(ctx, name, metav1.GetOptions{})
        if err != nil {
            return err
        }
        
        // Check if finalizer already exists
        for _, f := range pod.Finalizers {
            if f == finalizerName {
                return nil // Already has finalizer
            }
        }
        
        // Add finalizer
        pod.Finalizers = append(pod.Finalizers, finalizerName)
        
        // Update
        _, err = clientset.CoreV1().Pods(namespace).Update(ctx, pod, metav1.UpdateOptions{})
        return err
    })
}

func removeFinalizer(ctx context.Context, clientset kubernetes.Interface, namespace, name string) error {
    return retry.RetryOnConflict(retry.DefaultRetry, func() error {
        // Get latest version
        pod, err := clientset.CoreV1().Pods(namespace).Get(ctx, name, metav1.GetOptions{})
        if err != nil {
            return err
        }
        
        // Remove finalizer
        var newFinalizers []string
        for _, f := range pod.Finalizers {
            if f != finalizerName {
                newFinalizers = append(newFinalizers, f)
            }
        }
        pod.Finalizers = newFinalizers
        
        // Update
        _, err = clientset.CoreV1().Pods(namespace).Update(ctx, pod, metav1.UpdateOptions{})
        return err
    })
}

func handleFinalization(ctx context.Context, clientset kubernetes.Interface, pod *corev1.Pod) error {
    // Check if object is being deleted
    if pod.DeletionTimestamp.IsZero() {
        // Not being deleted, ensure finalizer is present
        return addFinalizer(ctx, clientset, pod.Namespace, pod.Name)
    }
    
    // Object is being deleted
    // Check if our finalizer is present
    hasFinalizer := false
    for _, f := range pod.Finalizers {
        if f == finalizerName {
            hasFinalizer = true
            break
        }
    }
    
    if !hasFinalizer {
        return nil // Our finalizer already removed
    }
    
    // Perform cleanup
    log.Printf("Performing cleanup for pod: %s/%s", pod.Namespace, pod.Name)
    
    // Simulate cleanup work
    time.Sleep(2 * time.Second)
    
    // Remove finalizer to allow deletion
    return removeFinalizer(ctx, clientset, pod.Namespace, pod.Name)
}

func main() {
    config, err := rest.InClusterConfig()
    if err != nil {
        log.Fatal(err)
    }
    
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        log.Fatal(err)
    }
    
    ctx := context.Background()
    
    // Create a pod
    pod := &corev1.Pod{
        ObjectMeta: metav1.ObjectMeta{
            Name: "example-pod",
        },
        Spec: corev1.PodSpec{
            Containers: []corev1.Container{
                {
                    Name:  "nginx",
                    Image: "nginx:1.21",
                },
            },
        },
    }
    
    createdPod, err := clientset.CoreV1().Pods("default").Create(ctx, pod, metav1.CreateOptions{})
    if err != nil {
        log.Fatal(err)
    }
    
    // Add finalizer
    err = handleFinalization(ctx, clientset, createdPod)
    if err != nil {
        log.Fatal(err)
    }
    
    log.Println("Finalizer added, pod protected from immediate deletion")
    
    // Later, when deleting the pod
    err = clientset.CoreV1().Pods("default").Delete(ctx, "example-pod", metav1.DeleteOptions{})
    if err != nil {
        log.Fatal(err)
    }
    
    // Get pod to check deletion
    deletingPod, err := clientset.CoreV1().Pods("default").Get(ctx, "example-pod", metav1.GetOptions{})
    if err != nil && !errors.IsNotFound(err) {
        log.Fatal(err)
    }
    
    if !errors.IsNotFound(err) {
        // Handle finalization (cleanup and remove finalizer)
        err = handleFinalization(ctx, clientset, deletingPod)
        if err != nil {
            log.Fatal(err)
        }
        
        log.Println("Cleanup complete, pod will be deleted")
    }
}
```

## Summary

These examples demonstrate:

1. **Basic Operations**: CRUD operations with typed clients
2. **Watching**: Real-time monitoring of resource changes
3. **Controllers**: Building robust controllers with informers and work queues
4. **CRDs**: Working with Custom Resources using dynamic client
5. **Server-Side Apply**: Declarative resource management
6. **Leader Election**: High-availability controller patterns
7. **Ownership**: Managing related resources with owner references
8. **Finalizers**: Cleanup logic before resource deletion

For more examples, see:
- Official examples: `staging/src/k8s.io/client-go/examples/`
- Sample controller: https://github.com/kubernetes/sample-controller
- Community examples: https://github.com/kubernetes/client-go/tree/master/examples
