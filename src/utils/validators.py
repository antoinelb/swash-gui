import hashlib
import random
from typing import Any, Callable

import pydantic

############
# external #
############


def hash_config(ignore: list[str] = []) -> Callable[..., Any]:
    """
    Create a model validator that hashes the configuration.

    This validator computes a hash of the model's fields and sets it to the
    model's hash field. The hash can be used for caching and tracking changes.

    Parameters
    ----------
    ignore : list[str], default []
        List of field names to ignore when computing the hash

    Returns
    -------
    Callable
        A pydantic model validator function
    """

    def fct_(model: pydantic.BaseModel) -> pydantic.BaseModel:
        model.hash = _hash_config(  # pyright: ignore
            {
                key: val
                for key, val in model.model_dump().items()
                if key not in ignore
            },
            model.hash,  # pyright: ignore
        )
        return model

    return pydantic.model_validator(mode="after")(fct_)  # pyright: ignore


def parse_config(field: str, fct: Callable) -> Callable:  # pyright: ignore
    """
    Create a field validator that parses configuration.

    This validator handles different types of input values for a field,
    ensuring they are converted to the appropriate config object type.

    Parameters
    ----------
    field : str
        Name of the field to validate
    fct : Callable
        Function to parse the field value

    Returns
    -------
    Callable
        A pydantic field validator function
    """

    def fct_(
        cls: type[pydantic.BaseModel],  # pyright: ignore
        val: dict[str, Any] | pydantic.BaseModel | None,
    ) -> pydantic.BaseModel:
        if isinstance(val, pydantic.BaseModel):
            return val
        elif val is None:
            return fct()  # pyright: ignore
        else:
            return fct(val)  # pyright: ignore

    return pydantic.field_validator(field, mode="before")(fct_)


def set_field(field: str, value: Any) -> Callable:  # pyright: ignore
    """
    Create a field validator that sets a field to a fixed value.

    Parameters
    ----------
    field : str
        Name of the field to set
    value : Any
        Value to set the field to

    Returns
    -------
    Callable
        A pydantic field validator function
    """

    def fct_(
        cls: type[pydantic.BaseModel], val: Any  # pyright: ignore
    ) -> Any:
        return value

    return pydantic.field_validator(field, mode="before")(fct_)


def set_seed_if_missing(field: str) -> Callable:  # pyright: ignore
    """
    Create a field validator that sets a random seed if none is provided.

    Parameters
    ----------
    field : str
        Name of the seed field

    Returns
    -------
    Callable
        A pydantic field validator function that sets a random seed
        if the field's value is 0
    """

    def fct_(val: int) -> int:
        if val == 0:
            return random.randint(0, 100_000)  # nosec
        else:
            return val

    return pydantic.field_validator(field, mode="before")(fct_)


############
# internal #
############


def _hash_config(config: dict[str, Any], prev_hash: str = "") -> str:
    """
    Compute a hash for a configuration dictionary.

    Parameters
    ----------
    config : dict[str, Any]
        Configuration dictionary to hash
    prev_hash : str, default ""
        Previous hash to incorporate

    Returns
    -------
    str
        Hash string for the configuration
    """
    prev_hash_ = prev_hash.split("_")
    config = _prepare_config_for_hashing(config)
    hash_ = hashlib.sha256(str(config).encode()).hexdigest()[:8]
    if len(prev_hash_) == 2:
        return f"{hash_}_{prev_hash_[1]}"
    else:
        return hash_


def _prepare_config_for_hashing(config: Any) -> Any:
    """
    Prepare a configuration object for hashing by sorting and filtering.

    Parameters
    ----------
    config : Any
        Configuration object to prepare

    Returns
    -------
    Any
        Prepared configuration object
    """
    if isinstance(config, dict):
        return {
            key: _prepare_config_for_hashing(config[key])
            for key in sorted(config)
            if key != "hash"
        }
    elif isinstance(config, list):
        return [_prepare_config_for_hashing(x) for x in config]
    else:
        return config
