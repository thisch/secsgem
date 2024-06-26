#####################################################################
# testHsmsEquipmentHandler.py
#
# (c) Copyright 2013-2016, Benjamin Parzella. All rights reserved.
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

import threading
import unittest.mock

import pytest
from mock_protocol import MockProtocol
from mock_settings import MockSettings

import secsgem.hsms
import secsgem.secs


class TestSecsHandler(unittest.TestCase):
    def testSecsDecode(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.secs.SecsHandler(settings)

        packet = settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS01F02(["MDLN", "SOFTREV"]), 0
        )

        function = client.streams_functions.decode(packet)

        assert function.stream == 1
        assert function.function == 2
        assert function[0] == "MDLN"
        assert function[1] == "SOFTREV"

    def testSecsDecodeNone(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.secs.SecsHandler(settings)

        function = client.streams_functions.decode(None)

        assert function is None

    def testSecsDecodeInvalidStream(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.secs.SecsHandler(settings)

        packet = secsgem.hsms.HsmsMessage(secsgem.hsms.HsmsHeader(0, 0, 99), b"")
        with pytest.raises(ValueError):
            client.streams_functions.decode(packet)

    def testSecsDecodeInvalidFunction(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.secs.SecsHandler(settings)

        packet = secsgem.hsms.HsmsMessage(secsgem.hsms.HsmsHeader(0, 0, 99), b"")
        with pytest.raises(ValueError):
            client.streams_functions.decode(packet)

    def testStreamFunction(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.secs.SecsHandler(settings)

        function = client.stream_function(1, 1)

        assert function is secsgem.secs.functions.SecsS01F01

    def testStreamFunctionInvalidStream(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.secs.SecsHandler(settings)

        with pytest.raises(ValueError, match="No function found for S99F01"):
            client.stream_function(99, 1)

    def testStreamFunctionInvalidFunction(self):
        settings = MockSettings(MockProtocol)
        client = secsgem.secs.SecsHandler(settings)

        with pytest.raises(ValueError, match="No function found for S01F99"):
            client.stream_function(1, 99)


class TestSecsHandlerPassive(unittest.TestCase):
    def setUp(self):
        self.settings = MockSettings(MockProtocol)

        self.client = secsgem.secs.SecsHandler(self.settings)

        self.client.enable()

    def tearDown(self):
        self.client.disable()

    def handleS01F01(self, handler, packet):
        handler.send_response(secsgem.secs.functions.SecsS01F02(), packet.header.system)

    def testStreamFunctionReceiving(self):
        self.settings.protocol.simulate_connect()

        self.client.register_stream_function(1, 1, self.handleS01F01)

        # send s01e01
        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS01F01(), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 2

    def testStreamFunctionSending(self):
        self.settings.protocol.simulate_connect()

        # send s01e01
        clientCommandThread = threading.Thread(
            target=self.client.send_and_waitfor_response,
            args=(secsgem.secs.functions.SecsS01F01(),),
            name="TestSecsHandlerPassive_testStreamFunctionSending",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 1

        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(
                secsgem.secs.functions.SecsS01F02(), packet.header.system
            )
        )

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testStreamFunctionReceivingUnhandledFunction(self):
        self.settings.protocol.simulate_connect()

        # send s01e01
        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS01F01(), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 9
        assert packet.header.function == 5

    def testStreamFunctionReceivingExceptingCallback(self):
        self.settings.protocol.simulate_connect()

        f = unittest.mock.Mock(side_effect=Exception("testException"))

        self.client.register_stream_function(1, 1, f)

        # send s01e01
        system_id = self.settings.protocol.get_next_system_counter()
        self.settings.protocol.simulate_message(
            self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS01F01(), system_id)
        )

        packet = self.settings.protocol.expect_message(system_id=system_id)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 0

    def testDisableCeids(self):
        self.settings.protocol.simulate_connect()

        clientCommandThread = threading.Thread(
            target=self.client.disable_ceids, name="TestSecsHandlerPassive_testDisableCeids"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=37)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 37

        function = self.client.streams_functions.decode(packet)

        assert function["CEED"] == False
        assert function["CEID"].get() == []

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F38(secsgem.secs.data_items.ERACK.ACCEPTED), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testDisableCeidReports(self):
        self.settings.protocol.simulate_connect()

        clientCommandThread = threading.Thread(
            target=self.client.disable_ceid_reports, name="TestSecsHandlerPassive_testDisableCeidReports"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=33)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 33

        function = self.client.streams_functions.decode(packet)

        assert function["DATAID"] == 0
        assert function["DATA"].get() == []

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F34(secsgem.secs.data_items.DRACK.ACK), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testListSVsAll(self):
        self.settings.protocol.simulate_connect()

        clientCommandThread = threading.Thread(
            target=self.client.list_svs, name="TestSecsHandlerPassive_testListSVsAll"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=11)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 11

        function = self.client.streams_functions.decode(packet)

        assert function.get() == []

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS01F12([{"SVID": 1, "SVNAME": "SV1", "UNITS": "mm"}]), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testListSVsSpecific(self):
        self.settings.protocol.simulate_connect()

        clientCommandThread = threading.Thread(
            target=self.client.list_svs, args=([1],), name="TestSecsHandlerPassive_testListSVsSpecific"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=11)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 11

        function = self.client.streams_functions.decode(packet)

        assert function.get() == [1]

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS01F12([{"SVID": 1, "SVNAME": "SV1", "UNITS": "mm"}]), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testRequestSVs(self):
        self.settings.protocol.simulate_connect()

        clientCommandThread = threading.Thread(
            target=self.client.request_svs, args=([1],), name="TestSecsHandlerPassive_testRequestSVs"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=3)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 3

        function = self.client.streams_functions.decode(packet)

        assert function.get() == [1]

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS01F04([1337]), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testRequestSV(self):
        self.settings.protocol.simulate_connect()

        clientCommandThread = threading.Thread(
            target=self.client.request_sv, args=(1,), name="TestSecsHandlerPassive_testRequestSV"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=3)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 3

        function = self.client.streams_functions.decode(packet)

        assert function.get() == [1]

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS01F04([1337]), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testListECsAll(self):
        self.settings.protocol.simulate_connect()

        clientCommandThread = threading.Thread(
            target=self.client.list_ecs, name="TestSecsHandlerPassive_testListECsAll"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=29)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 29

        function = self.client.streams_functions.decode(packet)

        assert function.get() == []

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F30(
                [
                    {
                        "ECID": 1,
                        "ECNAME": "EC1",
                        "ECMIN": secsgem.secs.variables.U1(0),
                        "ECMAX": secsgem.secs.variables.U1(100),
                        "ECDEF": secsgem.secs.variables.U1(50),
                        "UNITS": "mm",
                    }
                ]
            ),
            packet.header.system,
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testListECsSpecific(self):
        self.settings.protocol.simulate_connect()

        clientCommandThread = threading.Thread(
            target=self.client.list_ecs, args=([1],), name="TestSecsHandlerPassive_testListECsSpecific"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=29)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 29

        function = self.client.streams_functions.decode(packet)

        assert function.get() == [1]

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F30(
                [
                    {
                        "ECID": 1,
                        "ECNAME": "EC1",
                        "ECMIN": secsgem.secs.variables.U1(0),
                        "ECMAX": secsgem.secs.variables.U1(100),
                        "ECDEF": secsgem.secs.variables.U1(50),
                        "UNITS": "mm",
                    }
                ]
            ),
            packet.header.system,
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testRequestECs(self):
        self.settings.protocol.simulate_connect()

        clientCommandThread = threading.Thread(
            target=self.client.request_ecs, args=([1],), name="TestSecsHandlerPassive_testRequestECs"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=13)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 13

        function = self.client.streams_functions.decode(packet)

        assert function.get() == [1]

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F14([1337]), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testRequestEC(self):
        self.settings.protocol.simulate_connect()

        clientCommandThread = threading.Thread(
            target=self.client.request_ec, args=(1,), name="TestSecsHandlerPassive_testRequestEC"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=13)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 13

        function = self.client.streams_functions.decode(packet)

        assert function.get() == [1]

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F14([1337]), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testSetECs(self):
        self.settings.protocol.simulate_connect()

        clientCommandThread = threading.Thread(
            target=self.client.set_ecs, args=([[1, "1337"]],), name="TestSecsHandlerPassive_testSetECs"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=15)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 15

        function = self.client.streams_functions.decode(packet)

        assert function.get() == [{"ECID": 1, "ECV": "1337"}]

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F16(secsgem.secs.data_items.EAC.ACK), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testSetEC(self):
        self.settings.protocol.simulate_connect()

        clientCommandThread = threading.Thread(
            target=self.client.set_ec, args=(1, 1337), name="TestSecsHandlerPassive_testSetEC"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=15)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 2
        assert packet.header.function == 15

        function = self.client.streams_functions.decode(packet)

        assert function.get() == [{"ECV": 1337, "ECID": 1}]

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS02F16(secsgem.secs.data_items.EAC.ACK), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testSendEquipmentTerminal(self):
        self.settings.protocol.simulate_connect()

        clientCommandThread = threading.Thread(
            target=self.client.send_equipment_terminal,
            args=(0, "Hello World"),
            name="TestSecsHandlerPassive_testSendEquipmentTerminal",
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=3)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 10
        assert packet.header.function == 3

        function = self.client.streams_functions.decode(packet)

        assert function.TID.get() == 0
        assert function.TEXT.get() == "Hello World"

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS10F04(secsgem.secs.data_items.ACKC10.ACCEPTED), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testAreYouThere(self):
        self.settings.protocol.simulate_connect()

        clientCommandThread = threading.Thread(
            target=self.client.are_you_there, name="TestSecsHandlerPassive_testAreYouThere"
        )
        clientCommandThread.daemon = True  # make thread killable on program termination
        clientCommandThread.start()

        packet = self.settings.protocol.expect_message(function=1)

        assert packet is not None
        assert packet.header.session_id == 0
        assert packet.header.stream == 1
        assert packet.header.function == 1

        packet = self.settings.protocol.create_message_for_function(
            secsgem.secs.functions.SecsS01F02([]), packet.header.system
        )
        self.settings.protocol.simulate_message(packet)

        clientCommandThread.join(1)
        assert not clientCommandThread.is_alive()

    def testUnhandeledFunctionCallback(self):
        self.settings.protocol.simulate_connect()

        f = unittest.mock.Mock(return_value=False)
        self.client.register_stream_function(1, 2, f)

        system_id = self.settings.protocol.get_next_system_counter()
        packet = self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS01F02([]), system_id)
        self.settings.protocol.simulate_message(packet)

    def testExceptionFunctionCallback(self):
        self.settings.protocol.simulate_connect()

        f = unittest.mock.Mock(side_effect=Exception("testException"))
        self.client.register_stream_function(1, 2, f)

        system_id = self.settings.protocol.get_next_system_counter()
        packet = self.settings.protocol.create_message_for_function(secsgem.secs.functions.SecsS01F02([]), system_id)
        self.settings.protocol.simulate_message(packet)

    def testUnregisterStreamFunctionCallback(self):
        f = unittest.mock.Mock()

        self.client.register_stream_function(0, 0, f)
        assert self.client._generate_sf_callback_name(0, 0) in self.client._callback_handler._callbacks

        self.client.unregister_stream_function(0, 0)
        assert self.client._generate_sf_callback_name(0, 0) not in self.client._callback_handler._callbacks

    def testRegisterCallback(self):
        f = unittest.mock.Mock()

        self.client.callbacks.test = f
        assert "test" in self.client.callbacks._callbacks

    def testCallbackIn(self):
        f = unittest.mock.Mock()

        self.client.callbacks.test = f
        assert "test" in self.client.callbacks

    def testCallCallback(self):
        f = unittest.mock.Mock()

        self.client.callbacks.test = f
        assert "test" in self.client._callback_handler._callbacks

        self.client.callbacks.test()

        f.assert_called_once()

    def testUnRegisterCallback(self):
        f = unittest.mock.Mock()

        self.client.callbacks.test = f
        assert "test" in self.client._callback_handler._callbacks

        self.client.callbacks.test = None
        assert "test" not in self.client._callback_handler._callbacks


class TestSecsHandlerActive(unittest.TestCase):
    def setUp(self):
        self.settings = MockSettings(MockProtocol)

        self.client = secsgem.secs.SecsHandler(self.settings)

        self.client.enable()

    def tearDown(self):
        self.client.disable()
