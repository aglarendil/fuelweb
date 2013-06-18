# -*- coding: utf-8 -*-

import json

import web

from nailgun.errors import errors
from nailgun.api.models import Release
from nailgun.api.validators.release import ReleaseValidator
from nailgun.api.handlers.base import JSONHandler, content_json


class ReleaseHandler(JSONHandler):
    fields = (
        "id",
        "name",
        "version",
        "description"
    )
    model = Release
    validator = ReleaseValidator

    @content_json
    def GET(self, release_id):
        release = self.get_object_or_404(Release, release_id)
        return self.render(release)

    @content_json
    def PUT(self, release_id):
        release = self.get_object_or_404(Release, release_id)

        data = self.checked_data()

        for key, value in data.iteritems():
            setattr(release, key, value)
        self.db.commit()
        return self.render(release)

    def DELETE(self, release_id):
        release = self.get_object_or_404(Release, release_id)
        self.db.delete(release)
        self.db.commit()
        raise web.webapi.HTTPError(
            status="204 No Content",
            data=""
        )


class ReleaseCollectionHandler(JSONHandler):

    validator = ReleaseValidator

    @content_json
    def GET(self):
        return map(
            ReleaseHandler.render,
            self.db.query(Release).all()
        )

    @content_json
    def POST(self):
        data = self.checked_data()

        release = Release()
        for key, value in data.iteritems():
            setattr(release, key, value)
        self.db.add(release)
        self.db.commit()
        raise web.webapi.created(json.dumps(
            ReleaseHandler.render(release),
            indent=4
        ))
