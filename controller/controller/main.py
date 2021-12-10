import logging

import kopf
from kubernetes import client
from hulk_deployment import HulkDeployment
from hulk_deployment import Mode

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


@kopf.on.create("hulkdeployments")
@kopf.on.update('hulkdeployments')
def hd_handler(body, **kwargs):
    hd = HulkDeployment.from_body(body)
    hd.sync()
    logger.info("Updated HulkDeployment name=%s in ns=%s,", hd.name, hd.namespace)


@kopf.on.delete('hulkdeployments')
def hd_delete_fn(body, **kwargs):
    hd = HulkDeployment.from_body(body)
    hd.mode = Mode.DEFAULT
    hd.sync()
    logger.info("Deleted Hulk Deployment name=%s in ns=%s", hd.name, hd.namespace)


def create_selector(d):
    selector = ''
    for k, v in d.items():
        selector += k + '=' + v + ','
    selector = selector[:-1]
    return selector


def process_fury(body):
    fury_mode = body["spec"]["mode"]
    fury_selector = body["spec"]["selector"]
    ns = body["metadata"]["namespace"]

    label_selector = create_selector(fury_selector)

    patch = {"spec": {"mode": fury_mode}}
    with client.ApiClient() as api_client:
        api_instance = client.CustomObjectsApi(api_client)
        group = "marvel.org"
        version = "v1"
        plural = "furys"
        print(label_selector)
        hulks = api_instance.list_namespaced_custom_object(group, version, ns, "hulkdeployments", label_selector=label_selector)
        print(hulks)
        for hulk in hulks["items"]:
            name = hulk["metadata"]["name"]
            api_instance.patch_namespaced_custom_object(group, version, ns, "hulkdeployments", name, patch)


@kopf.on.update("fury")
@kopf.on.create("fury")
def fury_handler(body, **kwargs):
    fury_name = body["metadata"]["name"]
    ns = body["metadata"]["namespace"]
    process_fury(body)
    logger.info("Update fury name=%s in ns=%s", fury_name, ns)


@kopf.on.delete("fury")
def furry_delete_fn(body,**kwargs):
    fury_name = body["metadata"]["name"]
    ns = body["metadata"]["namespace"]
    body["spec"]["mode"] = "default"
    process_fury(body)
    logger.info("Deleted fury name=%s in ns=%s", fury_name, ns)
