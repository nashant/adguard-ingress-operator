from kopf import Logger
from typing import Callable, Dict, List
from adguardhome import AdGuardHome


async def add_rule(
    ag: AdGuardHome,
    rule: Dict[str, str],
    rewrites: List[Dict[str, str]],
    logger: Logger
) -> None:
    rule_str = f"{rule['domain']}->{rule['answer']}"
    if rule in rewrites:
        logger.info(f"Rule {rule_str} already exists on {ag.host}")
        return
    await ag.request("/control/rewrite/add", method="POST", json_data=rule)
    logger.info(f"Rule {rule_str} added on {ag.host}")


async def delete_rule(
    ag: AdGuardHome,
    rule: Dict[str, str],
    rewrites: List[Dict[str, str]],
    logger: Logger
) -> None:
    rule_str = f"{rule['domain']}->{rule['answer']}"
    if rule not in rewrites:
        logger.info(f"Rule {rule_str} not found on {ag.host}")
        return
    await ag.request("/control/rewrite/delete", method="POST", json_data=rule)
    logger.info(f"Rule {rule_str} deleted from {ag.host}")


async def process_rules(
    config: Dict[str, str],
    rules: List[Dict[str, str]],
    op: Callable,
    logger: Logger
) -> None:
    async with AdGuardHome(**config) as ag:
        rewrites = await ag.request("/control/rewrite/list")
        for rule in rules:
            await op(ag, rule, rewrites, logger)
