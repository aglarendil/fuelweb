# -*- coding: utf-8 -*-

import web

from nailgun.api.models import Node
from nailgun.api.models import NetworkAssignment
from nailgun.api.models import NodeNICInterface

from nailgun.logger import logger


class TopoChecker(object):
    @classmethod
    def _is_assignment_allowed_for_node(cls, node):
        db_node = self.db.query(Node).filter_by(id=node['id']).first()
        interfaces = node['interfaces']
        db_interfaces = db_node.interfaces
        allowed_network_ids = set([n.id for n in db_node.allowed_networks])
        for iface in interfaces:
            db_iface = filter(
                lambda i: i.id == iface['id'],
                db_interfaces
            )
            db_iface = db_iface[0]
            for net in iface['assigned_networks']:
                if net['id'] not in allowed_network_ids:
                    return False
        return True

    @classmethod
    def is_assignment_allowed(cls, data):
        for node in data:
            if not cls._is_assignment_allowed_for_node(node):
                return False
        return True

    @classmethod
    def resolve_topo_conflicts(cls, data):
        raise NotImplementedError("Will be implemented later")
