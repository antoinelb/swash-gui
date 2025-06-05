import argparse
from math import pi, sqrt
from typing import TypedDict, cast

#########
# types #
#########

c_c = 0.611
c_v = 0.98
g = 9.81


class Cylinder(TypedDict):
    radius: tuple[float, float]


class Rectangle(TypedDict):
    length: tuple[float, float]
    width: tuple[float, float]


class Inputs(TypedDict):
    shape: Cylinder | Rectangle
    height: tuple[float, float]
    orifice_height: tuple[float, float]
    orifice_radius: tuple[float, float]


##################
# inputs parsing #
##################


def main() -> None:
    inputs_ = _parse_inputs()
    inputs = cast(
        Inputs,
        {
            "shape": _parse_shape(inputs_.base),
            "height": _parse_number(inputs_.hauteur, "La hauteur"),
            "orifice_height": _parse_number(
                inputs_.emplacement, "L'emplacement de l'orifice"
            ),
            "orifice_radius": _parse_number(
                inputs_.rayon, "Le rayon de l'orifice"
            ),
        },
    )

    time, delta_time = compute_time(inputs)

    print(f"t = {time:.2f} ± {delta_time:.2f} s")


def _parse_inputs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(conflict_handler="resolve")
    parser.add_argument(
        "-b",
        "--base",
        help="Forme de la base soit de la forme #±# pour un cylindre ou #±#x#±# pour un prisme rectangulaire, où # représente un nombre, le premier nombre est la valeur et le deuxième l'incertitude.",
    )
    parser.add_argument(
        "-h",
        "--hauteur",
        help="Hauteur du réservoir de la forme #±# où le premier # est la valeur et le deuxième l'incertitude sur cette valeur.",
    )
    parser.add_argument(
        "-e",
        "--emplacement",
        help="Hauteur de l'emplacement de l'orifice de la forme #±# où le premier # est la valeur et le deuxième l'incertitude sur cette valeur. Une valeur de 0 indique que l'orifice est sur la face inférieure et toute autre valeur qu'il est sur une face latérale.",
    )
    parser.add_argument(
        "-r",
        "--rayon",
        help="Rayon de l'orifice de la forme #±# où le premier # est la valeur et le deuxième l'incertitude sur cette valeur.",
    )
    return parser.parse_args()


def _parse_shape(shape: str) -> Cylinder | Rectangle:
    shape_ = shape.split("x")
    if len(shape_) not in (1, 2):
        raise ValueError(
            "La base doit être de la forme #±# ou #±#x#±x. Voir --help."
        )
    if len(shape_) == 2:
        return {
            "length": _parse_number(shape_[0], "La longueur"),
            "width": _parse_number(shape_[1], "La largeur"),
        }
    else:
        return {"radius": _parse_number(shape_[0], "Le rayon")}


def _parse_number(number: str, key: str) -> tuple[float, float]:
    number_ = number.split("±")
    try:
        val = float(number_[0])
        uncertainty = float(number_[1])
    except (IndexError, ValueError):
        raise ValueError(f"{key} doit être de la forme #±#. Voir --help.")
    return val, uncertainty


################
# calculations #
################


def compute_time(inputs: Inputs) -> tuple[float, float]:
    if inputs["orifice_height"] >= inputs["height"]:
        time, delta_time = 0.0, 0.0
    else:
        if "radius" in inputs["shape"]:
            time = _compute_cylinder_time(inputs)
            delta_time = _compute_cylinder_delta_time(inputs)
        else:
            time = _compute_rectangular_time(inputs)
            delta_time = _compute_rectangular_delta_time(inputs)

    return time, delta_time


def _compute_cylinder_time(inputs: Inputs) -> float:
    R = inputs["shape"]["radius"][0]  # type: ignore
    r = inputs["orifice_radius"][0] / 1000  # conversion de mm à m
    H = inputs["height"][0]
    h = inputs["orifice_height"][0]
    return (
        R**2
        * sqrt(2 * (1 - c_c**3 * (r / R) ** 4))
        / (c_v * c_c * r**2 * sqrt(g))
        * (sqrt(H) - sqrt(h))
    )


def _compute_cylinder_delta_time(inputs: Inputs) -> float:
    R = inputs["shape"]["radius"][0]  # type: ignore
    delta_R = inputs["shape"]["radius"][1]  # type: ignore
    r = inputs["orifice_radius"][0] / 1000  # conversion de mm à m
    delta_r = inputs["orifice_radius"][1] / 1000  # conversion de mm à m
    H = inputs["height"][0]
    delta_H = inputs["height"][1]
    h = inputs["orifice_height"][0]
    delta_h = inputs["orifice_height"][1]

    return abs(
        sqrt(2)
        * R**2
        / (c_v * c_c * r**2 * sqrt(g * (1 - c_c**3 * (r / R) ** 4)))
    ) * (
        abs(2 * (sqrt(H) - sqrt(h)) * (1 + c_c**3 * (r / R) ** 4) / R)
        * delta_R
        + abs(-2 * (sqrt(H) - sqrt(h)) * (1 + c_c**3 * (r / R) ** 4) / r)
        * delta_r
        + abs((1 - c_c**3 * (r / R) ** 4) / sqrt(2 * H)) * delta_H
        + (
            abs(-(1 - c_c**3 * (r / R) ** 4) / sqrt(2 * h)) * delta_h
            if h != 0
            else 0
        )
    )


def _compute_rectangular_time(inputs: Inputs) -> float:
    L = inputs["shape"]["length"][0]  # type: ignore
    l = inputs["shape"]["width"][0]  # type: ignore # noqa
    r = inputs["orifice_radius"][0] / 1000  # conversion de mm à m
    H = inputs["height"][0]
    h = inputs["orifice_height"][0]
    return (
        L
        * l
        * sqrt(2 * (1 - c_c**3 * pi**2 * r**4 / (L**2 * l**2)))
        / (c_v * c_c * pi * r**2 * sqrt(g))
        * (sqrt(H) - sqrt(h))
    )


def _compute_rectangular_delta_time(inputs: Inputs) -> float:
    L = inputs["shape"]["length"][0]  # type: ignore
    delta_L = inputs["shape"]["length"][1]  # type: ignore
    l = inputs["shape"]["width"][0]  # type: ignore # noqa
    delta_l = inputs["shape"]["width"][1]  # type: ignore
    r = inputs["orifice_radius"][0] / 1000  # conversion de mm à m
    delta_r = inputs["orifice_radius"][1] / 1000  # conversion de mm à m
    H = inputs["height"][0]
    delta_H = inputs["height"][1]
    h = inputs["orifice_height"][0]
    delta_h = inputs["orifice_height"][1]

    return abs(
        sqrt(2)
        * L
        * l
        / (
            c_v
            * c_c
            * pi
            * r**2
            * sqrt(g * (1 - c_c**3 * pi**2 * r**4 / (L**2 * l**2)))
        )
    ) * (
        abs(
            (sqrt(H) - sqrt(h))
            * (1 + c_c**3 * pi**2 * r**4 / (L**2 * l**2))
            / (L * l)
        )
        * (abs(l) * delta_L + abs(L) * delta_l)
        + abs(
            -2
            * (sqrt(H) - sqrt(h))
            * (1 + c_c**3 * pi**2 * r**4 / (L**2 * l**2))
            / r
        )
        * delta_r
        + abs((1 - c_c**3 * pi**2 * r**4 / (L**2 * l**2)) / sqrt(2 * H))
        * delta_H
        + (
            abs(-(1 - c_c**3 * pi**2 * r**4 / (L**2 * l**2)) / sqrt(2 * h))
            * delta_h
            if h != 0
            else 0
        )
    )


if __name__ == "__main__":
    main()
