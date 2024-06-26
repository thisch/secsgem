#####################################################################
# handler.py
#
# (c) Copyright 2013-2023, Benjamin Parzella. All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#####################################################################
"""Handler for SECS commands."""

from __future__ import annotations

import logging
import typing

import secsgem.common
from secsgem.secs.functions import SecsS01F04, SecsS01F12, StreamsFunctions

if typing.TYPE_CHECKING:
    from .data_items import SV


class SecsHandler:  # pylint: disable=too-many-instance-attributes,too-many-public-methods
    """Baseclass for creating Host/Equipment models. This layer contains the SECS functionality.

    Inherit from this class and override required functions.
    """

    def __init__(self, settings: secsgem.common.Settings):
        """Initialize a secs handler.

        Args:
            settings: settings defining protocol and connection

        """
        self._settings = settings
        self.streams_functions = StreamsFunctions()

        self._protocol = settings.create_protocol(self.streams_functions)
        self._protocol.events.message_received += self._on_message_received

        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        self._callback_handler = secsgem.common.CallbackHandler()
        self._callback_handler.target = self

    @property
    def settings(self) -> secsgem.common.Settings:
        """Get the setting object."""
        return self._settings

    @staticmethod
    def _generate_sf_callback_name(stream: int, function: int) -> str:
        return f"s{stream:02d}f{function:02d}"

    @property
    def protocol(self) -> secsgem.common.Protocol:
        """Get the connection for the handler."""
        return self._protocol

    def enable(self):
        """Enable the connection."""
        self.protocol.enable()

    def disable(self):
        """Disable the connection."""
        self.protocol.disable()

    def send_response(self, *args, **kwargs):
        """Wrapper for connections send_response function."""
        return self.protocol.send_response(*args, **kwargs)

    def send_and_waitfor_response(self, *args, **kwargs):
        """Wrapper for connections send_and_waitfor_response function."""
        return self.protocol.send_and_waitfor_response(*args, **kwargs)

    def send_stream_function(self, *args, **kwargs):
        """Wrapper for connections send_stream_function function."""
        return self.protocol.send_stream_function(*args, **kwargs)

    @property
    def events(self):
        """Wrapper for connections events."""
        return self.protocol.events

    @property
    def callbacks(self):
        """Property for callback handling."""
        return self._callback_handler

    def register_stream_function(self, stream: int, function: int, callback):
        """Register the function callback for stream and function.

        :param stream: stream to register callback for
        :type stream: integer
        :param function: function to register callback for
        :type function: integer
        :param callback: method to call when stream and functions is received
        :type callback: def callback(connection)
        """
        name = self._generate_sf_callback_name(stream, function)
        setattr(self._callback_handler, name, callback)

    def unregister_stream_function(self, stream, function):
        """Unregister the function callback for stream and function.

        :param stream: stream to unregister callback for
        :type stream: integer
        :param function: function to register callback for
        :type function: integer
        """
        name = self._generate_sf_callback_name(stream, function)
        setattr(self._callback_handler, name, None)

    def _handle_stream_function(self, message):
        sf_callback_index = self._generate_sf_callback_name(message.header.stream, message.header.function)

        # return S09F05 if no callback present
        if sf_callback_index not in self._callback_handler:
            self.logger.warning("unexpected function received %s\n%s", sf_callback_index, message.header)
            if message.header.require_response:
                self.send_response(self.stream_function(9, 5)(message.header.encode()), message.header.system)

            return

        try:
            callback = getattr(self._callback_handler, sf_callback_index)
            result = callback(self, message)
            if result is not None:
                self.send_response(result, message.header.system)
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Callback aborted because of exception, abort sent")
            self.send_response(self.stream_function(message.header.stream, 0)(), message.header.system)

    def _on_message_received(self, data: dict[str, typing.Any]):
        """Message received from protocol layer.

        Args:
            data: received data

        """
        message = data["message"]

        # check if callbacks available for this stream and function
        self._handle_stream_function(message)

    def disable_ceids(self):
        """Disable all Collection Events."""
        self.logger.info("Disable all collection events")

        return self.send_and_waitfor_response(self.stream_function(2, 37)({"CEED": False, "CEID": []}))

    def disable_ceid_reports(self):
        """Disable all Collection Event Reports."""
        self.logger.info("Disable all collection event reports")

        return self.send_and_waitfor_response(self.stream_function(2, 33)({"DATAID": 0, "DATA": []}))

    def list_svs(self, svs: typing.Sequence[int | str] | None = None) -> SecsS01F12:
        """Get list of available Status Variables.

        :returns: available Status Variables
        :rtype: list
        """
        self.logger.info("Get list of status variables")

        if svs is None:
            svs = []

        message = self.send_and_waitfor_response(self.stream_function(1, 11)(svs))

        return typing.cast(SecsS01F12, self.streams_functions.decode(message))

    def request_svs(self, svs: typing.Sequence[int | str]) -> SecsS01F04:
        """Request contents of supplied Status Variables.

        :param svs: Status Variables to request
        :type svs: list
        :returns: values of requested Status Variables
        :rtype: list
        """
        self.logger.info("Get value of status variables %s", svs)

        message = self.send_and_waitfor_response(self.stream_function(1, 3)(svs))

        return typing.cast(SecsS01F04, self.streams_functions.decode(message))

    def request_sv(self, sv_id: int | str) -> SV:
        """Request contents of one Status Variable.

        :param sv_id: id of Status Variable
        :type sv_id: int
        :returns: value of requested Status Variable
        :rtype: various
        """
        self.logger.info("Get value of status variable %s", sv_id)

        return self.request_svs([sv_id]).data[0]

    def list_ecs(self, ecs=None):
        """Get list of available Equipment Constants.

        :returns: available Equipment Constants
        :rtype: list
        """
        self.logger.info("Get list of equipment constants")

        if ecs is None:
            ecs = []
        message = self.send_and_waitfor_response(self.stream_function(2, 29)(ecs))

        return self.streams_functions.decode(message)

    def request_ecs(self, ecs):
        """Request contents of supplied Equipment Constants.

        :param ecs: Equipment Constants to request
        :type ecs: list
        :returns: values of requested Equipment Constants
        :rtype: list
        """
        self.logger.info("Get value of equipment constants %s", ecs)

        message = self.send_and_waitfor_response(self.stream_function(2, 13)(ecs))

        return self.streams_functions.decode(message)

    def request_ec(self, ec_id):
        """Request contents of one Equipment Constant.

        :param ec_id: id of Equipment Constant
        :type ec_id: int
        :returns: value of requested Equipment Constant
        :rtype: various
        """
        self.logger.info("Get value of equipment constant %s", ec_id)

        return self.request_ecs([ec_id])

    def set_ecs(self, ecs):
        """Set contents of supplied Equipment Constants.

        :param ecs: list containing list of id / value pairs
        :type ecs: list
        """
        self.logger.info("Set value of equipment constants %s", ecs)

        message = self.send_and_waitfor_response(self.stream_function(2, 15)(ecs))

        return self.streams_functions.decode(message).get()

    def set_ec(self, ec_id, value):
        """Set contents of one Equipment Constant.

        :param ec_id: id of Equipment Constant
        :type ec_id: int
        :param value: new content of Equipment Constant
        :type value: various
        """
        self.logger.info("Set value of equipment constant %s to %s", ec_id, value)

        return self.set_ecs([[ec_id, value]])

    def send_equipment_terminal(self, terminal_id, text):
        """Set text to equipment terminal.

        :param terminal_id: ID of terminal
        :type terminal_id: int
        :param text: text to send
        :type text: string
        """
        self.logger.info("Send text to terminal %s", terminal_id)

        return self.send_and_waitfor_response(self.stream_function(10, 3)({"TID": terminal_id, "TEXT": text}))

    def are_you_there(self):
        """Check if remote is still replying."""
        self.logger.info("Requesting 'are you there'")

        return self.send_and_waitfor_response(self.stream_function(1, 1)())

    def stream_function(self, stream: int, function: int) -> type[secsgem.secs.SecsStreamFunction]:
        """Get class for stream and function.

        Args:
            stream: stream to get class for
            function: function to get class for

        Returns:
            class for function

        """
        return self.streams_functions.function(stream, function)
