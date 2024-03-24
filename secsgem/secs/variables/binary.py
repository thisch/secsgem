#####################################################################
# binary.py
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
"""SECS binary variable type."""

from .base import Base


class Binary(Base):
    """Secs type for binary data."""

    format_code = 0o10
    text_code = "B"
    preferred_types = [bytes, bytearray]

    def __init__(self, value=None, count=-1):
        """Initialize a binary secs variable.

        :param value: initial value
        :type value: string/integer
        :param count: number of items this value
        :type count: integer
        """
        super().__init__()

        self.value = bytearray()
        self.count = count
        if value is not None:
            self.set(value)

    def __repr__(self):
        """Generate textual representation for an object of this class."""
        if len(self.value) == 0:
            return f"<{self.text_code}>"

        data = " ".join(f"0x{c:x}" for c in self.value)

        return f"<{self.text_code} {data.strip()}>"

    def __len__(self):
        """Get the length."""
        return len(self.value)

    def __getitem__(self, key):
        """Get an item using the indexer operator."""
        if key >= self.count:
            raise IndexError(f"Index {key} out of bounds ({self.count})")

        if key >= len(self.value):
            return 0

        return self.value[key]

    def __setitem__(self, key, item):
        """Set an item using the indexer operator."""
        if key >= self.count:
            raise IndexError(f"Index {key} out of bounds ({self.count})")

        if key >= len(self.value):
            while key >= len(self.value):
                self.value.append(0)

        self.value[key] = item

    def __eq__(self, other):
        """Check equality with other object."""
        if isinstance(other, Base):
            if other.is_dynamic:
                return other.value.value == self.value
            return other.value == self.value

        return other == self.value

    def __hash__(self):
        """Get data item for hashing."""
        return hash(bytes(self.value))

    @staticmethod
    def _check_single_item_support(value):
        if isinstance(value, bool):
            return True

        if isinstance(value, int):
            if 0 <= value <= 255:
                return True
            return False

        return False

    def supports_value(self, value) -> bool:
        """Check if the current instance supports the provided value.

        :param value: value to test
        :type value: any
        """
        if isinstance(value, (list, tuple)):
            return self._supports_value_list(value)

        if isinstance(value, bytearray):
            return self._supports_value_bytearray(value)

        if isinstance(value, bytes):
            return self._supports_value_bytes(value)

        if isinstance(value, str):
            return self._supports_value_str(value)

        return self._check_single_item_support(value)

    def _supports_value_list(self, value) -> bool:
        if self.count > 0 and len(value) > self.count:
            return False
        return all(self._check_single_item_support(item) for item in value)

    def _supports_value_bytearray(self, value) -> bool:
        if self.count > 0 and len(value) > self.count:
            return False
        return True

    def _supports_value_bytes(self, value) -> bool:
        if self.count > 0 and len(value) > self.count:
            return False
        return True

    def _supports_value_str(self, value) -> bool:
        if self.count > 0 and len(value) > self.count:
            return False
        try:
            value.encode("ascii")
        except UnicodeEncodeError:
            return False

        return True

    def set(self, value):
        """Set the internal value to the provided value.

        :param value: new value
        :type value: string/integer
        """
        if value is None:
            return

        if isinstance(value, bytes):
            value = bytearray(value)
        elif isinstance(value, str):
            value = bytearray(value.encode("ascii"))
        elif isinstance(value, (list, tuple)):
            value = bytearray(value)
        elif isinstance(value, bytearray):
            pass
        elif isinstance(value, int):
            if 0 <= value <= 255:
                value = bytearray([value])
            else:
                raise ValueError(
                    f"Value {value} of type {type(value).__name__} is out of range for {self.__class__.__name__}"
                )
        else:
            raise TypeError(f"Unsupported type {type(value).__name__} for {self.__class__.__name__}")

        if 0 < self.count < len(value):
            raise ValueError(f"Value longer than {self.count} chars ({len(value)} chars)")

        self.value = value

    def get(self):
        """Return the internal value.

        :returns: internal value
        :rtype: list/integer
        """
        if len(self.value) == 1:
            return self.value[0]

        return bytes(self.value)

    def encode(self):
        """Encode the value to secs data.

        :returns: encoded data bytes
        :rtype: string
        """
        result = self.encode_item_header(len(self.value) if self.value is not None else 0)

        if self.value is not None:
            result += bytes(self.value)

        return result

    def decode(self, data, start=0):
        """Decode the secs byte data to the value.

        :param data: encoded data bytes
        :type data: string
        :param start: start position of value the data
        :type start: integer
        :returns: new start position
        :rtype: integer
        """
        (text_pos, _, length) = self.decode_item_header(data, start)

        # string
        result = None

        if length > 0:
            result = data[text_pos : text_pos + length]

        self.set(result)

        return text_pos + length
