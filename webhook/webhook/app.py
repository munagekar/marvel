import base64
import copy
import http
import logging
import os
import time

import jsonpatch  # type: ignore
from kubernetes import client, config
from kubernetes.client import V1ResourceRequirements
from flask import Flask, jsonify, request

app = Flask(__name__)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

config.load_incluster_config()


def v1_resources_to_json(r:V1ResourceRequirements):
    d = {}
    requests = r.requests
    limits = r.limits

    if requests:
        d["requests"] = requests

    if limits:
        d["limits"] = limits

    return d


def get_deployment(name, ns):
    api = client.AppsV1Api()
    deployments = api.list_namespaced_deployment(namespace=ns)
    for d in deployments.items:
        if d.metadata.name == name:
            return d
    raise RuntimeError(f"Deployment name={name} not found in namespace={ns}")


@app.route("/mutate/hulkdeployment", methods=["POST"])
def mutate():
    start_time = time.time()

    hd = request.json["request"]["object"]
    hd_spec = hd["spec"]

    hd_orig = copy.deepcopy(hd)

    name = hd["metadata"]["name"]
    ns = hd["metadata"]["namespace"]
    hd_id = f"{ns}/{name}"
    logger.info(f"Got a Request for hulkdeployment %s", hd_id)

    target_deployment = hd_spec["deploymentName"]
    target_deployment = get_deployment(target_deployment, ns)

    if "default" not in hd_spec:
        hd_spec["default"] = {}

    if "replicas" not in hd_spec["default"]:
        hd_spec["default"]["replicas"] = target_deployment.spec.replicas

    if "containers" not in hd_spec["default"]:
        containers = []
        for container in target_deployment.spec.template.spec.contain_config:
            if container.resources:
                name = container.name
                resources = v1_resources_to_json(container.resources)
                containers.append({"name": name, "resources": resources})
        hd_spec["default"]["containers"] = containers

    if "hulk" not in hd_spec:
        hd_spec["hulk"] = copy.deepcopy(hd_spec["default"])

    if "replicas" not in hd_spec["hulk"]:
        hd_spec["hulk"]["replicas"] = target_deployment.spec.replicas

    if "containers" not in hd_spec["hulk"]:
        hd_spec["hulk"]["containers"] = hd_spec["default"]["containers"]

    # Set Resource Requests to Limits
    for container in hd_spec["hulk"]["containers"]:
        if not container["resources"]["limits"]:
            container["resources"]["limits"] = container["resources"]["requests"]

    patch = jsonpatch.JsonPatch.from_diff(hd_orig, hd)
    print(patch)

    end_time = time.time()
    time_ms = int((end_time - start_time) * 1000)
    logger.info("Returned Response for %s in %s ms", hd_id, time_ms)
    return jsonify(
        {
            "response": {
                "allowed": True,
                "uid": request.json["request"]["uid"],
                "patch": base64.b64encode(str(patch).encode()).decode(),
                "patchtype": "JSONPatch",
            }
        }
    )


@app.route("/health", methods=["GET"])
def health():
    logger.debug("Got Health Request")
    return ("", http.HTTPStatus.NO_CONTENT)


if __name__ == "__main__":
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=LOG_LEVEL)
    app.run(host="0.0.0.0", debug=True)  # pragma: no cover
