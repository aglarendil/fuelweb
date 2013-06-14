# -*- coding: utf-8 -*-

import web

from nailgun.logger import logger


class NailgunException(Exception):

    def __init__(self,
                 message="",
                 log_traceback=False,
                 log_message=False,
                 log_level='warning',
                 notify_user=False):
        self.log_traceback = log_traceback
        self.log_message = log_message
        self.notify_user = notify_user
        if message:
            self.message = message

            client = self._get_client()
            if client:
                self.message = "[{0}] ".format(client) + self.message

            if self.log_message:
                getattr(logger, log_level)(self.message)
        super(NailgunException, self).__init__()

    def _get_client(self):
        """
        web.ctx.env is a thread-local object,
        this hack is for getting client IP to add it
        inside error message
        """
        if not hasattr(web.ctx, "env"):
            return None

        if 'HTTP_X_REAL_IP' in web.ctx.env:
            return web.ctx.env['HTTP_X_REAL_IP']
        elif 'REMOTE_ADDR' in web.ctx.env:
            return web.ctx.env['REMOTE_ADDR']
        else:
            return None

    def __str__(self):
        return self.message

    def __unicode__(self):
        return self.message
