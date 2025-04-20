# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
from asdf.tags.core.ndarray import NDArrayType

from astropy import table
from astropy.io.misc.asdf.types import AstropyAsdfType, AstropyType


class TableType:
    """
    This class defines to_tree and from_tree methods that are used by both the
    AstropyTableType and the AsdfTableType defined below. The behavior is
    differentiated by the ``_compat`` class attribute. When ``_compat==True``,
    the behavior will conform to the table schema defined by the ASDF Standard.
    Otherwise, the behavior will conform to the custom table schema defined by
    Astropy.
    """

    _compat = False

    @classmethod
    def from_tree(cls, node, ctx):
        """
        Generate a `~astropy.table.Table` or `~astropy.table.QTable` from an ASDF node.
        
        This function creates a table from an ASDF node, using the specified context. It supports both standard `~astropy.table.Table` and `~astropy.table.QTable` based on the presence of a "qtable" flag in the node. The table's metadata is derived from the "meta" field in the node.
        
        Parameters
        ----------
        node : dict
        The
        """

        # This is getting meta, guys
        meta = node.get("meta", {})

        # This enables us to support files that use the table definition from
        # the ASDF Standard, rather than the custom one that Astropy defines.
        if cls._compat:
            return table.Table(node["columns"], meta=meta)

        if node.get("qtable", False):
            t = table.QTable(meta=node.get("meta", {}))
        else:
            t = table.Table(meta=node.get("meta", {}))

        for name, col in zip(node["colnames"], node["columns"]):
            t[name] = col

        return t

    @classmethod
    def to_tree(cls, data, ctx):
        columns = [data[name] for name in data.colnames]

        node = dict(columns=columns)
        # Files that use the table definition from the ASDF Standard (instead
        # of the one defined by Astropy) will not contain these fields
        if not cls._compat:
            node["colnames"] = data.colnames
            node["qtable"] = isinstance(data, table.QTable)
        if data.meta:
            node["meta"] = data.meta

        return node

    @classmethod
    def assert_equal(cls, old, new):
        """
        Asserts that two objects are equal by comparing their metadata and data.
        
        This function checks if the metadata of two objects are equal and then compares their data. If the objects are not arrays, it compares them directly. If the objects are arrays, it recursively compares each column or element.
        
        Parameters:
        old (object): The first object to compare.
        new (object): The second object to compare.
        
        Raises:
        AssertionError: If the metadata or data of the two objects do not match.
        
        This
        """

        assert old.meta == new.meta
        try:
            NDArrayType.assert_equal(np.array(old), np.array(new))
        except (AttributeError, TypeError, ValueError):
            for col0, col1 in zip(old, new):
                try:
                    NDArrayType.assert_equal(np.array(col0), np.array(col1))
                except (AttributeError, TypeError, ValueError):
                    assert col0 == col1


class AstropyTableType(TableType, AstropyType):
    """
    This tag class reads and writes tables that conform to the custom schema
    that is defined by Astropy (in contrast to the one that is defined by the
    ASDF Standard). The primary reason for differentiating is to enable the
    support of Astropy mixin columns, which are not supported by the ASDF
    Standard.
    """

    name = "table/table"
    types = ["astropy.table.Table"]
    requires = ["astropy"]


class AsdfTableType(TableType, AstropyAsdfType):
    """
    This tag class allows Astropy to read (and write) ASDF files that use the
    table definition that is provided by the ASDF Standard (instead of the
    custom one defined by Astropy). This is important to maintain for
    cross-compatibility.
    """

    name = "core/table"
    types = ["astropy.table.Table"]
    requires = ["astropy"]
    _compat = True


class ColumnType(AstropyAsdfType):
    name = "core/column"
    types = ["astropy.table.Column", "astropy.table.MaskedColumn"]
    requires = ["astropy"]
    handle_dynamic_subclasses = True

    @classmethod
    def from_tree(cls, node, ctx):
        """
        Generate a table.Column from a given tree node.
        
        This function creates a table.Column object from a dictionary representing a tree node. The dictionary should contain the following keys:
        - "data": The data to be included in the column, expected to be an array-like object.
        - "name": The name of the column.
        - "description": (Optional) A description of the column.
        - "unit": (Optional) The unit of the column's data.
        - "meta": (Optional) Metadata
        """

        data = node["data"]
        name = node["name"]
        description = node.get("description")
        unit = node.get("unit")
        meta = node.get("meta", None)

        return table.Column(
            data=data._make_array(),
            name=name,
            description=description,
            unit=unit,
            meta=meta,
        )

    @classmethod
    def to_tree(cls, data, ctx):
        """
        Generate a tree node representation from a given data object.
        
        This function takes a data object and constructs a dictionary representing a tree node. The node includes the data's name, data, and optionally its description, unit, and meta information.
        
        Parameters:
        data (Data): The data object to be converted into a tree node.
        ctx (Context): The context object containing necessary information for processing.
        
        Returns:
        dict: A dictionary representing the tree node with keys 'data', 'name', 'description
        """

        node = {
            "data": data.data,
            "name": data.name,
        }
        if data.description:
            node["description"] = data.description
        if data.unit:
            node["unit"] = data.unit
        if data.meta:
            node["meta"] = data.meta

        return node

    @classmethod
    def assert_equal(cls, old, new):
        assert old.meta == new.meta
        assert old.description == new.description
        assert old.unit == new.unit

        NDArrayType.assert_equal(np.array(old), np.array(new))
