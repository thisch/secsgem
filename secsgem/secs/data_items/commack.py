#####################################################################
# commack.py
#
# (c) Copyright 2021, Benjamin Parzella. All rights reserved.
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
"""COMMACK data item."""

from .. import variables
from .base import DataItemBase


class COMMACK(DataItemBase, variables.Binary):
    """Establish communications acknowledge.

    :Type: :class:`Binary <secsgem.secs.variables.Binary>`
    :Length: 1

    **Values**
        +-------+-------------------+---------------------------------------------------+
        | Value | Description       | Constant                                          |
        +=======+===================+===================================================+
        | 0     | Accepted          | :const:`secsgem.secs.data_items.COMMACK.ACCEPTED` |
        +-------+-------------------+---------------------------------------------------+
        | 1     | Denied, Try Again | :const:`secsgem.secs.data_items.COMMACK.DENIED`   |
        +-------+-------------------+---------------------------------------------------+
        | 2-63  | Reserved          |                                                   |
        +-------+-------------------+---------------------------------------------------+

    **Used In Function**
        - :class:`SecsS01F14 <secsgem.secs.functions.SecsS01F14>`

    """

    __type__ = variables.Binary
    __count__ = 1

    ACCEPTED = 0
    DENIED = 1
