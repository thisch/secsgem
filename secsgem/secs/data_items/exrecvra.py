#####################################################################
# exrecvra.py
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
"""EXRECVRA data item."""

from .. import variables
from .base import DataItemBase


class EXRECVRA(DataItemBase, variables.String):
    """Exception recovery action.

    :Type: :class:`String <secsgem.secs.variables.String>`
    :Length: 40

    **Used In Function**
        - :class:`SecsS05F09 <secsgem.secs.functions.SecsS05F09>`
        - :class:`SecsS05F13 <secsgem.secs.functions.SecsS05F13>`

    """

    __type__ = variables.String
    __count__ = 40
