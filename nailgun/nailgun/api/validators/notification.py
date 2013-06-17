# -*- coding: utf-8 -*-

from nailgun.db import orm
from nailgun.errors import errors
from nailgun.api.models import Notification
from nailgun.api.validators.base import BasicValidator


class NotificationValidator(BasicValidator):
    @classmethod
    def validate_update(cls, data):

        valid = {}
        d = cls.validate_json(data)

        status = d.get("status", None)
        if status in Notification.NOTIFICATION_STATUSES:
            valid["status"] = status
        else:
            raise errors.InvalidData(
                "Bad status",
                log_message=True
            )

        return valid

    @classmethod
    def validate_collection_update(cls, data):
        d = cls.validate_json(data)
        if not isinstance(d, list):
            raise errors.InvalidData(
                "Invalid json list",
                log_message=True
            )

        q = orm().query(Notification)
        valid_d = []
        for nd in d:
            valid_nd = {}
            if "id" not in nd:
                raise errors.InvalidData(
                    "ID is not set correctly",
                    log_message=True
                )

            if "status" not in nd:
                raise errors.InvalidData(
                    "ID is not set correctly",
                    log_message=True
                )

            if not q.get(nd["id"]):
                raise errors.InvalidData(
                    "Invalid ID specified",
                    log_message=True
                )

            valid_nd["id"] = nd["id"]
            valid_nd["status"] = nd["status"]
            valid_d.append(valid_nd)
        return valid_d
