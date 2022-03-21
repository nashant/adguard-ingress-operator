from kopf import Logger, Meta, Spec, Status, TemporaryError
from typing import Dict, List, Union

from util import HashableDict


def get_hosts(spec: Spec, ingress: str, logger: Logger) -> List[str]:
    try:
        return list(map(lambda r: r["host"], spec["rules"]))
    except KeyError:
        raise TemporaryError(f"No hosts found in {ingress}")


def get_ip(status: Status, ingress: str, logger: Logger, error_no_ip: bool) -> str:
    try:
        return status["loadBalancer"]["ingress"][0]["ip"]
    except KeyError:
        raise TemporaryError(f"IP not found in {ingress}")


def get_rules(
    meta: Meta,
    spec: Spec,
    status: Status,
    logger: Logger,
    error_no_ip: bool=True
) -> List[Dict[str, str]]:
    ingress = f"{meta['namespace']}/{meta['name']}"
    hosts = get_hosts(spec, ingress, logger)
    ip = get_ip(status, ingress, logger, error_no_ip)
    return set([HashableDict({"domain": host, "answer": ip}) for host in hosts])
