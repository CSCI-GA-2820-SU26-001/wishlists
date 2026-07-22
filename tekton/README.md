# Wishlist Tekton continuous delivery pipeline

This directory defines an in-cluster CD pipeline with four ordered stages:

1. `clone` checks out the requested Git revision.
2. `test` installs the locked development dependencies and runs the unit tests with the project's 95% coverage gate.
3. `build` uses Kaniko to build and push the image without a Docker daemon.
4. `deploy` applies the Kubernetes manifests, updates the image, and waits for the Deployment rollout to succeed.

## Prerequisites

- A Kubernetes cluster with Tekton Pipelines installed (the manifests use `tekton.dev/v1`).
- A registry reachable from both Tekton pods and Kubernetes nodes.
- Registry credentials when the target registry is private.

Install the reusable resources in the namespace where the pipeline will run. The example Role is namespace-scoped, so `deploy-namespace` must be that same namespace (use a separately reviewed RoleBinding in another namespace if cross-namespace deployment is required):

```bash
kubectl apply -f tekton/tasks.yaml
kubectl apply -f tekton/pipeline.yaml
kubectl apply -f tekton/rbac.yaml
```

Edit `tekton/pipelinerun.yaml` to set the Git revision, image name, deployment namespace, and registry security mode, then start a run:

```bash
kubectl create -f tekton/pipelinerun.yaml
tkn pipelinerun logs --last -f
```

For a TLS-enabled registry, set `insecure-registry` to `"false"`. For a private registry, create a Docker registry secret and attach it to the pipeline service account:

```bash
kubectl create secret docker-registry registry-credentials \
  --docker-server=REGISTRY \
  --docker-username=USERNAME \
  --docker-password=PASSWORD
kubectl patch serviceaccount wishlist-pipeline \
  -p '{"imagePullSecrets":[{"name":"registry-credentials"}],"secrets":[{"name":"registry-credentials"}]}'
```

Use an immutable tag such as the Git commit SHA for `image` in automated triggers. A failed test or build prevents all later stages from running; a failed rollout marks the PipelineRun as failed.
