# -*- coding: utf-8 -*-

from nailgun.db import orm
from nailgun.errors import errors
from nailgun.api.models import Node
from nailgun.volumes.manager import VolumeManager
from nailgun.api.validators.base import BasicValidator


class MetaInterfacesValidator(BasicValidator):
    @classmethod
    def _validate_data(cls, interfaces):
        if not isinstance(interfaces, list):
            raise errors.InvalidInterfacesInfo(
                "Meta.interfaces should be list",
                log_message=True
            )

        return interfaces

    @classmethod
    def validate_create(cls, interfaces):
        interfaces = cls._validate_data(interfaces)

        def filter_valid_nic(nic):
            for key in ('mac', 'name'):
                if not key in nic or not isinstance(nic[key], basestring)\
                        or not nic[key]:
                    return False
            return True

        return filter(filter_valid_nic, interfaces)

    @classmethod
    def validate_update(cls, interfaces):
        interfaces = cls._validate_data(interfaces)

        for nic in interfaces:
            if not isinstance(nic, dict):
                raise errors.InvalidInterfacesInfo(
                    "Interface in meta.interfaces must be dict",
                    log_message=True
                )

        return interfaces


class MetaValidator(BasicValidator):
    @classmethod
    def _validate_data(cls, meta):
        if not isinstance(meta, dict):
            raise errors.InvalidMetadata(
                "Invalid data: 'meta' should be dict",
                log_message=True
            )

    @classmethod
    def validate_create(cls, meta):
        cls._validate_data(meta)
        if 'interfaces' in meta:
            meta['interfaces'] = MetaInterfacesValidator.validate_create(
                meta['interfaces']
            )
        else:
            raise errors.InvalidInterfacesInfo(
                "Failed to discover node: "
                "invalid interfaces info",
                log_message=True
            )
        return meta

    @classmethod
    def validate_update(cls, meta):
        cls._validate_data(meta)
        if 'interfaces' in meta:
            meta['interfaces'] = MetaInterfacesValidator.validate_update(
                meta['interfaces']
            )
        return meta


class NodeValidator(BasicValidator):
    @classmethod
    def validate(cls, data):
        d = cls.validate_json(data)
        if not isinstance(d, dict):
            raise errors.InvalidData(
                "Node data must be dict",
                log_message=True
            )
        if not "mac" in d:
            raise errors.InvalidData(
                "No mac address specified",
                log_message=True
            )
        else:
            q = orm().query(Node)
            if q.filter(Node.mac == d["mac"]).first():
                raise errors.AlreadyExists(
                    "Node with mac {0} already "
                    "exists - doing nothing".format(d["mac"]),
                    log_level="info"
                )
            if cls.validate_existent_node_mac_post(d):
                raise errors.AlreadyExists(
                    "Node with mac {0} already "
                    "exists - doing nothing".format(d["mac"]),
                    log_level="info"
                )
        if "id" in d:
            del d["id"]
        if 'meta' in d:
            MetaValidator.validate_create(d['meta'])
        return d

    # TODO: fix this using DRY
    @classmethod
    def validate_existent_node_mac_post(cls, data):
        if 'meta' in data:
            data['meta'] = MetaValidator.validate_create(data['meta'])
            if 'interfaces' in data['meta']:
                existent_node = orm().query(Node).filter(Node.mac.in_(
                    [n['mac'] for n in data['meta']['interfaces']])).first()
                return existent_node

    @classmethod
    def validate_existent_node_mac_put(cls, data):
        if 'meta' in data:
            data['meta'] = MetaValidator.validate_update(data['meta'])
            if 'interfaces' in data['meta']:
                existent_node = orm().query(Node).filter(Node.mac.in_(
                    [n['mac'] for n in data['meta']['interfaces']])).first()
                return existent_node

    @classmethod
    def validate_update(cls, data):
        d = cls.validate_json(data)
        if "status" in d and d["status"] not in Node.NODE_STATUSES:
            raise errors.InvalidData(
                "Invalid status for node",
                log_message=True
            )
        if "id" in d:
            del d["id"]
        if 'meta' in d:
            d['meta'] = MetaValidator.validate_update(d['meta'])
        return d

    @classmethod
    def validate_collection_update(cls, data):
        d = cls.validate_json(data)
        if not isinstance(d, list):
            raise errors.InvalidData(
                "Invalid json list",
                log_message=True
            )

        q = orm().query(Node)
        for nd in d:
            if not "mac" in nd and not "id" in nd:
                raise errors.InvalidData(
                    "MAC or ID is not specified",
                    log_message=True
                )
            else:
                if "mac" in nd:
                    existent_node = q.filter_by(mac=nd["mac"]).first() \
                        or cls.validate_existent_node_mac_put(nd)
                    if not existent_node:
                        raise errors.InvalidData(
                            "Invalid MAC specified",
                            log_message=True
                        )
                if "id" in nd and not q.get(nd["id"]):
                    raise errors.InvalidData(
                        "Invalid ID specified",
                        log_message=True
                    )
            if 'meta' in nd:
                nd['meta'] = MetaValidator.validate_update(nd['meta'])
        return d


class NodeAttributesValidator(BasicValidator):
    pass


class NodeVolumesValidator(BasicValidator):
    @classmethod
    def validate(cls, data):
        # Here we instantiate VolumeManager with data
        # and during initialization it validates volumes.
        # So we can get validated volumes just after
        # VolumeManager initialization
        vm = VolumeManager(data=data)
        return vm.volumes
