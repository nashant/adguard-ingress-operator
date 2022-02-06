import kopf

from os import environ

from adguard import add_rule, delete_rule, process_rules
from ingress import get_rules
from util import config


@kopf.on.startup()
def configure(logger: kopf.Logger, settings: kopf.OperatorSettings, memo: kopf.Memo, **_):
    memo.config = config(environ.get("OPERATOR_CONFIG_FILE", "/app/config.yaml"))

    settings.persistence.finalizer = 'adguard-ingress-operator/kopf-finalizer'
    settings.persistence.progress_storage = kopf.AnnotationsProgressStorage(prefix='adguard-ingress-operator')
    settings.persistence.diffbase_storage = kopf.AnnotationsDiffBaseStorage(
        prefix='adguard-ingress-operator',
        key='last-handled-configuration',
    )


@kopf.on.create("ingress")
async def create_ingress(
    logger: kopf.Logger,
    meta: kopf.Meta,
    spec: kopf.Spec,
    status: kopf.Status,
    memo: kopf.Memo,
    **_,
):
    rules = get_rules(meta, spec, status, logger)
    for ag in memo.config["instances"]:
        await process_rules(ag, rules, add_rule, logger)


@kopf.on.update("ingress")
async def update_ingress(
    logger: kopf.Logger,
    meta: kopf.Meta,
    spec: kopf.Spec,
    status: kopf.Status,
    memo: kopf.Memo,
    old: dict,
    new: dict,
    **_,
):
    if status["loadBalancer"]["ingress"][0]["ip"] == None:
        return

    old_spec = old.get("spec", spec)
    old_status = old.get("status", status)
    old_rules = get_rules(meta, old_spec, old_status, logger)

    new_spec = new.get("spec", spec)
    new_status = new.get("status", status)
    new_rules = get_rules(meta, new_spec, new_status, logger)

    common_rules = old_rules.intersection(new_rules)
    old_rules = old_rules.difference(common_rules)
    new_rules = new_rules.difference(common_rules)

    for ag in memo.config["instances"]:
        await process_rules(ag, old_rules, delete_rule, logger)
        await process_rules(ag, new_rules, add_rule, logger)


@kopf.on.delete("ingress")
async def delete_ingress(
    logger: kopf.Logger,
    meta: kopf.Meta,
    spec: kopf.Spec,
    status: kopf.Status,
    memo: kopf.Memo,
    **_,
):
    rules = get_rules(meta, spec, status, logger)
    for ag in memo.config["instances"]:
        await process_rules(ag, rules, delete_rule, logger)
