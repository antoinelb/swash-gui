import tomllib
from pathlib import Path
from typing import cast

from starlette.requests import Request
from starlette.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
)
from starlette.routing import BaseRoute, Mount, Route
from starlette.staticfiles import StaticFiles

from src.platform import Inputs, compute_time

from .utils import with_query_string_params

#########
# types #
#########

pyproject_path = Path(__file__).parent / ".." / ".." / "pyproject.toml"
static_dir = Path(__file__).parent / ".." / "static"

############
# external #
############


def get_routes() -> list[BaseRoute]:
    return [
        Route("/", endpoint=_index, methods=["GET"]),
        Route("/ping", endpoint=_ping, methods=["GET"]),
        Route("/version", endpoint=_get_version, methods=["GET"]),
        Mount(
            "/static",
            app=StaticFiles(directory=str(static_dir.absolute())),
        ),
        Route("/compute", endpoint=_compute_time, methods=["GET"]),
    ]


############
# internal #
############


async def _ping(_: Request) -> Response:
    return PlainTextResponse("Pong!")


async def _get_version(_: Request) -> Response:
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    if "project" in config and "version" in config["project"]:
        return PlainTextResponse(config["project"]["version"])
    else:
        return PlainTextResponse("Unknown version", 500)


async def _index(_: Request) -> Response:
    with open(static_dir / "index.html") as f:
        index = f.read()
    return HTMLResponse(index)


@with_query_string_params(
    args=[
        "height",
        "orifice_height",
        "orifice_radius",
        "height_uncertainty",
        "orifice_height_uncertainty",
        "orifice_radius_uncertainty",
    ],
    opt_args=[
        "radius",
        "length",
        "width",
        "radius_uncertainty",
        "length_uncertainty",
        "width_uncertainty",
    ],
)
async def _compute_time(
    _: Request,
    height: str,
    orifice_height: str,
    orifice_radius: str,
    height_uncertainty: str,
    orifice_height_uncertainty: str,
    orifice_radius_uncertainty: str,
    radius: str | None = None,
    length: str | None = None,
    width: str | None = None,
    radius_uncertainty: str | None = None,
    length_uncertainty: str | None = None,
    width_uncertainty: str | None = None,
) -> Response:
    is_cylinder = radius is not None and radius_uncertainty is not None
    is_rectangle = (
        length is not None
        and width is not None
        and length_uncertainty is not None
        and width_uncertainty is not None
    )
    if is_cylinder == is_rectangle:
        return PlainTextResponse(
            "Soit le rayon du cylindre doit être donné, ou la longueur et largeur du prisme rectangulaire, avec dans les deux cas l'incertitude associée à la mesure.",
            status_code=400,
        )

    if is_cylinder:
        shape = {
            "radius": (float(radius), float(radius_uncertainty))  # type: ignore
        }
    else:
        shape = {
            "length": (float(length), float(length_uncertainty)),  # type: ignore
            "width": (float(width), float(width_uncertainty)),  # type: ignore
        }

    inputs = cast(
        Inputs,
        {
            "shape": shape,
            "height": (float(height), float(height_uncertainty)),
            "orifice_height": (
                float(orifice_height),
                float(orifice_height_uncertainty),
            ),
            "orifice_radius": (
                float(orifice_radius),
                float(orifice_radius_uncertainty),
            ),
        },
    )

    time, delta_time = compute_time(inputs)

    return JSONResponse({"time": time, "delta_time": delta_time})
