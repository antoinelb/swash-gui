from math import cosh, pi, tanh

#########
# types #
#########

g = 9.81

############
# external #
############


def compute_wavelength(
    wave_period: float, water_depth: float, *, n_iter: int = 50
) -> float:
    """
    Compute wavelength for a single wave period using the dispersion relation.

    Uses Newton-Raphson method to solve the implicit dispersion relation:
    L = (g * T^2) / (2 * pi) * tanh(2 * pi * h / L)

    Parameters
    ----------
    wave_period : float
        Wave period in seconds.
    water_depth : float
        Water depth in meters.
    n_iter : int, optional
        Number of Newton-Raphson iterations, by default 50.

    Returns
    -------
    float
        Wavelength in meters.
    """
    L = water_depth / 0.05
    for _ in range(n_iter):
        L = L - _compute_dispersion_relation(
            L, water_depth, wave_period
        ) / _compute_dispersion_relation_derivative(
            L, water_depth, wave_period
        )
    return L


############
# internal #
############


def _compute_dispersion_relation(L: float, h: float, T: float) -> float:
    """
    Compute the dispersion relation function for Newton-Raphson iteration.

    Parameters
    ----------
    L : float
        Current wavelength estimate in meters.
    h : float
        Water depth in meters.
    T : float
        Wave period in seconds.

    Returns
    -------
    float
        Value of the dispersion relation function.
    """
    return L - g * T**2 / (2 * pi) * tanh(2 * pi * h / L)


def _compute_dispersion_relation_derivative(
    L: float, h: float, T: float
) -> float:
    """
    Compute the derivative of the dispersion relation for Newton-Raphson iteration.

    Parameters
    ----------
    L : float
        Current wavelength estimate in meters.
    h : float
        Water depth in meters.
    T : float
        Wave period in seconds.

    Returns
    -------
    float
        Derivative of the dispersion relation function.
    """
    return g * h * T**2 / (cosh(2 * pi * h / L) ** 2 * L**2) + 1
