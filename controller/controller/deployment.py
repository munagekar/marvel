import kubernetes


def get_deployment(name, ns):
    api = kubernetes.client.AppsV1Api()
    deployments = api.list_namespaced_deployment(namespace=ns)
    for d in deployments.items:
        if d.metadata.name == name:
            return d
    raise RuntimeError(f"Deployment name={name} not found in namespace={ns}")


def patch_deployment(name,ns,deployment):
    api = kubernetes.client.AppsV1Api()
    api.patch_namespaced_deployment(name,ns,deployment)


