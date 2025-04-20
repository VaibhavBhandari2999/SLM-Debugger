# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.io.misc.asdf.types import AstropyAsdfType
from astropy.units import Unit, UnitBase


class UnitType(AstropyAsdfType):
    name = "unit/unit"
    types = ["astropy.units.UnitBase"]
    requires = ["astropy"]

    @classmethod
    def to_tree(cls, node, ctx):
        """
        Convert a given node to a string representation in the 'vounit' format.
        
        This method handles different types of input and converts them to a string representation suitable for the 'vounit' format. It supports both strings and instances of `UnitBase`. If the input is a string, it first attempts to parse it as a `Unit` object. If the input is already a `UnitBase` instance, it converts it directly to a string. If the input is neither a string nor
        """

        if isinstance(node, str):
            node = Unit(node, format="vounit", parse_strict="warn")
        if isinstance(node, UnitBase):
            return node.to_string(format="vounit")
        raise TypeError(f"'{node}' is not a valid unit")

    @classmethod
    def from_tree(cls, node, ctx):
        return Unit(node, format="vounit", parse_strict="silent")
