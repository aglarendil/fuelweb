# -*- coding: utf-8 -*-

import json

from nailgun.errors import errors


class BasicValidator(object):
    @classmethod
    def validate_json(cls, data, desired_type=None):
        if data:
            try:
                res = json.loads(data)
            except:
                raise errors.InvalidData(
                    "Invalid json received",
                    log_message=True
                )
            if desired_type and not isinstance(res, desired_type):
                raise errors.InvalidData(
                    "Invalid data received (expected {0})".format(
                        str(desired_type)
                    ),
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
        raise NotImplementedError("You should override this method")
