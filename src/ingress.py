from kopf import Logger, Meta, Spec, Status
from typing import Dict, List, Union

from util import HashableDict


def get_hosts(spec: Spec, ingress: str, logger: Logger) -> List[str]:
    try:
        return list(map(lambda r: r["host"], spec["rules"]))
    except KeyError:
        logger.warn(f"No hosts found in {ingress}")
        return []


def get_ip(status: Status, ingress: str, logger: Logger) -> Union[str, None]:
    try:
        return status["loadBalancer"]["ingress"][0]["ip"]
    except KeyError:
        logger.warn(f"IP not found in {ingress}")
        return None


def get_rules(
    meta: Meta,
    spec: Spec,
    status: Status,
    logger: Logger
) -> List[Dict[str, str]]:
    ingress = f"{meta['namespace']}/{meta['name']}"
    hosts = get_hosts(spec, ingress, logger)
    ip = get_ip(status, ingress, logger)
    return set([HashableDict({"domain": host, "answer": ip}) for host in hosts])
