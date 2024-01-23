#!/usr/bin/python3
# coding=utf-8

#   Copyright 2024 getcarrier.io
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

""" SIO """

from pylon.core.tools import log  # pylint: disable=E0611,E0401,W0611
from pylon.core.tools import web  # pylint: disable=E0611,E0401


class SIO:  # pylint: disable=E1101,R0903
    """
        SIO Resource

        self is pointing to current Module instance

        web.sio decorator takes one argument: event name
        Note: web.sio decorator must be the last decorator (at top)

        SIO resources use sio_check auth decorator
        auth.decorators.sio_check takes the following arguments:
        - permissions
        - scope_id=1
    """

    @web.sio("connect")
    def eventnode_connect(self, sid, environ):
        """ Event handler """
        _ = environ
        #
        self.clients[sid] = {
            "auth": False,
            "room": "eventnode:default",
        }

    @web.sio("disconnect")
    def eventnode_disconnect(self, sid):
        """ Event handler """
        client = self.clients.pop(sid, None)
        #
        if client and client["auth"]:
            self.context.sio.leave_room(sid, client["room"])

    @web.sio("eventnode_join")
    def eventnode_join(self, sid, data):
        """ Event handler """
        if sid not in self.clients:
            return
        #
        if not isinstance(data, dict):
            return
        #
        if data.get("password", "") == self.descriptor.config.get("password", ""):
            self.clients[sid]["auth"] = True
        else:
            return
        #
        if "room" in data:
            room = f'eventnode:{data["room"]}'
            self.clients[sid]["room"] = room
        #
        self.context.sio.enter_room(sid, self.clients[sid]["room"])
        #
        log.info("EventNode %s joined %s", sid, self.clients[sid]["room"])

    @web.sio("eventnode_event")
    def eventnode_event(self, sid, data):
        """ Event handler """
        if sid not in self.clients:
            return
        #
        if not self.clients[sid]["auth"]:
            return
        #
        self.context.sio.emit(
            event="eventnode_event",
            data=data,
            room=self.clients[sid]["room"],
        )
