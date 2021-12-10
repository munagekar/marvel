from enum import Enum, auto
from dataclasses import dataclass
from deployment import get_deployment, patch_deployment


class Mode(Enum):
    HULK = auto()
    DEFAULT = auto()

    @classmethod
    def str_to_mode(cls, mode: str):
        if mode.lower() == "hulk":
            return Mode.HULK

        if mode.lower() == "default":
            return Mode.DEFAULT

        raise ValueError(f"Got invalid mode={mode}")


@dataclass
class Config:
    replicas: int
    container_config: dict

    @classmethod
    def from_spec(cls, spec: dict):
        replicas = spec["replicas"]
        container_config = {c["name"]: c["resources"] for c in spec["containers"]}
        return Config(replicas=replicas, container_config=container_config)


@dataclass
class HulkDeployment:
    name: str
    namespace: str
    mode: Mode
    deployment_name: str
    default_config: Config
    hulk_config: Config

    @classmethod
    def from_spec(cls, hd_spec: dict, name, ns):
        mode = Mode.str_to_mode(hd_spec["mode"])
        deployment_name = hd_spec["deploymentName"]

        hulk_config = Config.from_spec(hd_spec["hulk"])
        default_config = Config.from_spec(hd_spec["default"])

        return cls(name, ns, mode, deployment_name, default_config, hulk_config)

    @classmethod
    def from_body(cls, hd):
        ns = hd["metadata"]["namespace"]
        name = hd["metadata"]["name"]
        return cls.from_spec(hd["spec"], name, ns)

    def sync(self):
        if self.mode == Mode.HULK:
            config = self.hulk_config
        else:
            config = self.default_config

        # patch replicas
        deployment = get_deployment(self.deployment_name, self.namespace)
        deployment.spec.replicas = config.replicas

        # patch containers
        for container in deployment.spec.template.spec.containers:
            container_name = container.name
            if container_name in config.container_config:
                correct_config = config.container_config[container_name]
                if "requests" in correct_config:
                    container.resources.requests = correct_config["requests"]
                if "limits" in correct_config:
                    container.resources.limits = correct_config["limits"]

        patch_deployment(self.deployment_name, self.namespace, deployment)
