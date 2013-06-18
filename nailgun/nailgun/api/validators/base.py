# -*- coding: utf-8 -*-

import json

from nailgun.errors import errors


class BasicValidator(object):
    @classmethod
    def validate_json(cls, data):
        if data:
            try:
                res = json.loads(data)
            except:
                raise errors.InvalidData(
                    "Invalid json received",
                    log_message=True
                )
        else:
            raise errors.InvalidData(
                "Empty request received",
                log_message=True
            )
        return res

    @classmethod
    def validate(cls, data):
        return cls.validate_json(data)
