#####################################################################
# testHsmsPacket.py
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

import secsgem.hsms

import unittest


class TestHsmsSelectReqHeader(unittest.TestCase):
    def testEncode(self):
        header = secsgem.hsms.HsmsSelectReqHeader(123)

        self.assertEqual(header.encode(), b"\xff\xff\x00\x00\x00\x01\x00\x00\x00{")

    def testEncodePacket(self):
        packet = secsgem.hsms.HsmsMessage(secsgem.hsms.HsmsSelectReqHeader(123), b"")

        self.assertEqual(packet.blocks[0].encode(), b"\x00\x00\x00\n\xff\xff\x00\x00\x00\x01\x00\x00\x00{")

    def testDecode(self):
        block = secsgem.hsms.HsmsBlock.decode(b"\x00\x00\x00\n\xff\xff\x00\x00\x00\x01\x00\x00\x00{")

        packet = secsgem.hsms.HsmsMessage.from_block(block)

        self.assertIsInstance(packet, secsgem.hsms.HsmsMessage)
        self.assertIsInstance(packet.header, secsgem.hsms.HsmsHeader)
        self.assertEqual(packet.header.function, 0)
        self.assertEqual(packet.header.stream, 0)
        self.assertEqual(packet.header.p_type, 0)
        self.assertEqual(packet.header.s_type.value, 1)
        self.assertEqual(packet.header.require_response, False)
        self.assertEqual(packet.header.system, 123)
        self.assertEqual(packet.header.session_id, 0xFFFF)


class TestHsmsSelectRspHeader(unittest.TestCase):
    def testEncode(self):
        header = secsgem.hsms.HsmsSelectRspHeader(123)

        self.assertEqual(header.encode(), b"\xff\xff\x00\x00\x00\x02\x00\x00\x00{")

    def testEncodePacket(self):
        packet = secsgem.hsms.HsmsMessage(secsgem.hsms.HsmsSelectRspHeader(123), b"")

        self.assertEqual(packet.blocks[0].encode(), b"\x00\x00\x00\n\xff\xff\x00\x00\x00\x02\x00\x00\x00{")

    def testDecode(self):
        block = secsgem.hsms.HsmsBlock.decode(b"\x00\x00\x00\n\xff\xff\x00\x00\x00\x02\x00\x00\x00{")

        packet = secsgem.hsms.HsmsMessage.from_block(block)

        self.assertIsInstance(packet, secsgem.hsms.HsmsMessage)
        self.assertIsInstance(packet.header, secsgem.hsms.HsmsHeader)
        self.assertEqual(packet.header.function, 0)
        self.assertEqual(packet.header.stream, 0)
        self.assertEqual(packet.header.p_type, 0)
        self.assertEqual(packet.header.s_type.value, 2)
        self.assertEqual(packet.header.require_response, False)
        self.assertEqual(packet.header.system, 123)
        self.assertEqual(packet.header.session_id, 0xFFFF)


class TestHsmsDeselectReqHeader(unittest.TestCase):
    def testEncode(self):
        header = secsgem.hsms.HsmsDeselectReqHeader(123)

        self.assertEqual(header.encode(), b"\xff\xff\x00\x00\x00\x03\x00\x00\x00{")

    def testEncodePacket(self):
        packet = secsgem.hsms.HsmsMessage(secsgem.hsms.HsmsDeselectReqHeader(123), b"")

        self.assertEqual(packet.blocks[0].encode(), b"\x00\x00\x00\n\xff\xff\x00\x00\x00\x03\x00\x00\x00{")

    def testDecode(self):
        block = secsgem.hsms.HsmsBlock.decode(b"\x00\x00\x00\n\xff\xff\x00\x00\x00\x03\x00\x00\x00{")

        packet = secsgem.hsms.HsmsMessage.from_block(block)

        self.assertIsInstance(packet, secsgem.hsms.HsmsMessage)
        self.assertIsInstance(packet.header, secsgem.hsms.HsmsHeader)
        self.assertEqual(packet.header.function, 0)
        self.assertEqual(packet.header.stream, 0)
        self.assertEqual(packet.header.p_type, 0)
        self.assertEqual(packet.header.s_type.value, 3)
        self.assertEqual(packet.header.require_response, False)
        self.assertEqual(packet.header.system, 123)
        self.assertEqual(packet.header.session_id, 0xFFFF)


class TestHsmsDeselectRspHeader(unittest.TestCase):
    def testEncode(self):
        header = secsgem.hsms.HsmsDeselectRspHeader(123)

        self.assertEqual(header.encode(), b"\xff\xff\x00\x00\x00\x04\x00\x00\x00{")

    def testEncodePacket(self):
        packet = secsgem.hsms.HsmsMessage(secsgem.hsms.HsmsDeselectRspHeader(123), b"")

        self.assertEqual(packet.blocks[0].encode(), b"\x00\x00\x00\n\xff\xff\x00\x00\x00\x04\x00\x00\x00{")

    def testDecode(self):
        block = secsgem.hsms.HsmsBlock.decode(b"\x00\x00\x00\n\xff\xff\x00\x00\x00\x04\x00\x00\x00{")

        packet = secsgem.hsms.HsmsMessage.from_block(block)

        self.assertIsInstance(packet, secsgem.hsms.HsmsMessage)
        self.assertIsInstance(packet.header, secsgem.hsms.HsmsHeader)
        self.assertEqual(packet.header.function, 0)
        self.assertEqual(packet.header.stream, 0)
        self.assertEqual(packet.header.p_type, 0)
        self.assertEqual(packet.header.s_type.value, 4)
        self.assertEqual(packet.header.require_response, False)
        self.assertEqual(packet.header.system, 123)
        self.assertEqual(packet.header.session_id, 0xFFFF)


class TestHsmsLinktestReqHeader(unittest.TestCase):
    def testEncode(self):
        header = secsgem.hsms.HsmsLinktestReqHeader(123)

        self.assertEqual(header.encode(), b"\xff\xff\x00\x00\x00\x05\x00\x00\x00{")

    def testEncodePacket(self):
        packet = secsgem.hsms.HsmsMessage(secsgem.hsms.HsmsLinktestReqHeader(123), b"")

        self.assertEqual(packet.blocks[0].encode(), b"\x00\x00\x00\n\xff\xff\x00\x00\x00\x05\x00\x00\x00{")

    def testDecode(self):
        block = secsgem.hsms.HsmsBlock.decode(b"\x00\x00\x00\n\xff\xff\x00\x00\x00\x05\x00\x00\x00{")

        packet = secsgem.hsms.HsmsMessage.from_block(block)

        self.assertIsInstance(packet, secsgem.hsms.HsmsMessage)
        self.assertIsInstance(packet.header, secsgem.hsms.HsmsHeader)
        self.assertEqual(packet.header.function, 0)
        self.assertEqual(packet.header.stream, 0)
        self.assertEqual(packet.header.p_type, 0)
        self.assertEqual(packet.header.s_type.value, 5)
        self.assertEqual(packet.header.require_response, False)
        self.assertEqual(packet.header.system, 123)
        self.assertEqual(packet.header.session_id, 0xFFFF)


class TestHsmsLinktestRspHeader(unittest.TestCase):
    def testEncode(self):
        header = secsgem.hsms.HsmsLinktestRspHeader(123)

        self.assertEqual(header.encode(), b"\xff\xff\x00\x00\x00\x06\x00\x00\x00{")

    def testEncodePacket(self):
        packet = secsgem.hsms.HsmsMessage(secsgem.hsms.HsmsLinktestRspHeader(123), b"")

        self.assertEqual(packet.blocks[0].encode(), b"\x00\x00\x00\n\xff\xff\x00\x00\x00\x06\x00\x00\x00{")

    def testDecode(self):
        block = secsgem.hsms.HsmsBlock.decode(b"\x00\x00\x00\n\xff\xff\x00\x00\x00\x06\x00\x00\x00{")

        packet = secsgem.hsms.HsmsMessage.from_block(block)

        self.assertIsInstance(packet, secsgem.hsms.HsmsMessage)
        self.assertIsInstance(packet.header, secsgem.hsms.HsmsHeader)
        self.assertEqual(packet.header.function, 0)
        self.assertEqual(packet.header.stream, 0)
        self.assertEqual(packet.header.p_type, 0)
        self.assertEqual(packet.header.s_type.value, 6)
        self.assertEqual(packet.header.require_response, False)
        self.assertEqual(packet.header.system, 123)
        self.assertEqual(packet.header.session_id, 0xFFFF)


class TestHsmsRejectReqHeader(unittest.TestCase):
    def testEncode(self):
        header = secsgem.hsms.HsmsRejectReqHeader(123, secsgem.hsms.HsmsSType.SELECT_REQ, 1)

        self.assertEqual(header.encode(), b"\xff\xff\x01\x01\x00\x07\x00\x00\x00{")

    def testEncodePacket(self):
        packet = secsgem.hsms.HsmsMessage(
            secsgem.hsms.HsmsRejectReqHeader(123, secsgem.hsms.HsmsSType.SELECT_REQ, 1), b""
        )

        self.assertEqual(packet.blocks[0].encode(), b"\x00\x00\x00\n\xff\xff\x01\x01\x00\x07\x00\x00\x00{")

    def testDecode(self):
        block = secsgem.hsms.HsmsBlock.decode(b"\x00\x00\x00\n\xff\xff\x01\x01\x00\x07\x00\x00\x00{")

        packet = secsgem.hsms.HsmsMessage.from_block(block)

        self.assertIsInstance(packet, secsgem.hsms.HsmsMessage)
        self.assertIsInstance(packet.header, secsgem.hsms.HsmsHeader)
        self.assertEqual(packet.header.function, 1)
        self.assertEqual(packet.header.stream, 1)
        self.assertEqual(packet.header.p_type, 0)
        self.assertEqual(packet.header.s_type.value, 7)
        self.assertEqual(packet.header.require_response, False)
        self.assertEqual(packet.header.system, 123)
        self.assertEqual(packet.header.session_id, 0xFFFF)


class TestHsmsSeparateReqHeader(unittest.TestCase):
    def testEncode(self):
        header = secsgem.hsms.HsmsSeparateReqHeader(123)

        self.assertEqual(header.encode(), b"\xff\xff\x00\x00\x00\t\x00\x00\x00{")

    def testEncodePacket(self):
        packet = secsgem.hsms.HsmsMessage(secsgem.hsms.HsmsSeparateReqHeader(123), b"")

        self.assertEqual(packet.blocks[0].encode(), b"\x00\x00\x00\n\xff\xff\x00\x00\x00\t\x00\x00\x00{")

    def testDecode(self):
        block = secsgem.hsms.HsmsBlock.decode(b"\x00\x00\x00\n\xff\xff\x00\x00\x00\t\x00\x00\x00{")

        packet = secsgem.hsms.HsmsMessage.from_block(block)

        self.assertIsInstance(packet, secsgem.hsms.HsmsMessage)
        self.assertIsInstance(packet.header, secsgem.hsms.HsmsHeader)
        self.assertEqual(packet.header.function, 0)
        self.assertEqual(packet.header.stream, 0)
        self.assertEqual(packet.header.p_type, 0)
        self.assertEqual(packet.header.s_type.value, 9)
        self.assertEqual(packet.header.require_response, False)
        self.assertEqual(packet.header.system, 123)
        self.assertEqual(packet.header.session_id, 0xFFFF)


class TestHsmsStreamFunctionHeader(unittest.TestCase):
    def testEncode(self):
        header = secsgem.hsms.HsmsStreamFunctionHeader(123, 1, 1, True, 100)

        self.assertEqual(header.encode(), b"\x00d\x81\x01\x00\x00\x00\x00\x00{")

    def testEncodePacket(self):
        packet = secsgem.hsms.HsmsMessage(secsgem.hsms.HsmsStreamFunctionHeader(123, 1, 1, True, 100), b"")

        self.assertEqual(packet.blocks[0].encode(), b"\x00\x00\x00\n\x00d\x81\x01\x00\x00\x00\x00\x00{")

    def testDecode(self):
        block = secsgem.hsms.HsmsBlock.decode(b"\x00\x00\x00\n\x00d\x81\x01\x00\x00\x00\x00\x00{")

        packet = secsgem.hsms.HsmsMessage.from_block(block)

        self.assertIsInstance(packet, secsgem.hsms.HsmsMessage)
        self.assertIsInstance(packet.header, secsgem.hsms.HsmsHeader)
        self.assertEqual(packet.header.function, 1)
        self.assertEqual(packet.header.stream, 1)
        self.assertEqual(packet.header.p_type, 0)
        self.assertEqual(packet.header.s_type.value, 0)
        self.assertEqual(packet.header.require_response, True)
        self.assertEqual(packet.header.system, 123)
        self.assertEqual(packet.header.session_id, 100)


class TestHsmsPacket(unittest.TestCase):
    def testRepr(self):
        block = secsgem.hsms.HsmsBlock.decode(b"\x00\x00\x00\n\x00d\x81\x01\x00\x00\x00\x00\x00{")
        packet = secsgem.hsms.HsmsMessage.from_block(block)

        assert (
            packet.__repr__()
            == "HsmsMessage({'header': HsmsHeader({session_id:0x0064, stream:01, function:01, p_type:0x00, s_type:0x00, system:0x0000007b, require_response:True}), 'data': ''})"
        )

    def testStr(self):
        block = secsgem.hsms.HsmsBlock.decode(b"\x00\x00\x00\n\x00d\x81\x01\x00\x00\x00\x00\x00{")
        packet = secsgem.hsms.HsmsMessage.from_block(block)

        assert (
            str(packet)
            == "'header': {session_id:0x0064, stream:01, function:01, p_type:0x00, s_type:0x00, system:0x0000007b, require_response:True} "
        )
