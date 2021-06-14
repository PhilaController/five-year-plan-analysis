import json
from pathlib import Path
from typing import Dict, Optional, Type, TypeVar, Union

import desert
import pandas as pd

# Create a generic variable that can be 'Parent', or any subclass.
T = TypeVar("T", bound="DataclassSchema")


class DataclassSchema:
    """Base class to handled serializing and deserializing dataclasses."""

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        """
        Return a new class instance from a dictionary
        representation.

        Parameters
        ----------
        data :
            The dictionary representation of the class.
        """
        schema = desert.schema(cls)
        return schema.load(data)

    @classmethod
    def from_json(cls: Type[T], path_or_json: Union[str, Path]) -> T:
        """
        Return a new class instance from either a file path
        or a valid JSON string.

        Parameters
        ----------
        path_or_json :
            Either the path of the file to load or a valid JSON string.
        """

        # Convert to Path() first to check
        _path = path_or_json
        if isinstance(_path, str):
            _path = Path(_path)
            if not _path.exists():
                raise FileNotFoundError(f"No such file: '{_path}'")
        assert isinstance(_path, Path)

        d = None
        try:  # catch file error too long
            if _path.exists():
                d = json.load(_path.open("r"))
        except OSError:
            pass
        finally:
            if d is None:
                d = json.loads(str(path_or_json))

        return cls.from_dict(d)

    def to_dict(self) -> dict:
        """Return a dictionary representation of the data."""
        schema = desert.schema(self.__class__)
        return schema.dump(self)

    def to_json(self, path: Optional[Union[str, Path]] = None) -> Optional[str]:
        """
        Serialize the object to JSON, either returning a valid JSON
        string or saving to the input file path.

        Parameters
        ----------
        path :
            the file path to save the JSON encoding to
        """

        # Dump to a dictionary
        schema = desert.schema(self.__class__)
        d = schema.dump(self)

        if path is None:
            return json.dumps(d)
        else:
            if isinstance(path, str):
                path = Path(path)
            json.dump(
                d, path.open("w"),
            )

            return None

