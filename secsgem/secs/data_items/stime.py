#####################################################################
# stime.py
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
"""STIME data item."""

from .. import variables
from .base import DataItemBase


class STIME(DataItemBase, variables.String):
    """Sample time.

    :Type: :class:`String <secsgem.secs.variables.String>`

    **Used In Function**
        - :class:`SecsS06F01 <secsgem.secs.functions.SecsS06F01>`

    """
