import numpy as np
import polars as pl


def calculate_wave_heights(
    water_levels: np.ndarray, timestep: float, method: str = "zero_crossing"
) -> dict:
    """
    Calculate wave statistics from water level time series.

    Parameters
    ----------
    water_levels : np.ndarray
        Water level time series
    timestep : float
        Time step between measurements in seconds
    method : str
        Method for wave detection ('zero_crossing' or 'peak')

    Returns
    -------
    dict
        Dictionary containing:
        - significant_wave_height: H1/3 (average of highest 1/3 of waves)
        - mean_wave_height: Mean of all wave heights
        - max_wave_height: Maximum wave height
        - rms_wave_height: Root mean square wave height
        - n_waves: Number of waves detected
        - mean_period: Mean wave period
    """
    if method == "zero_crossing":
        wave_heights, wave_periods = _zero_crossing_analysis(
            water_levels, timestep
        )
    else:
        raise ValueError(f"Unknown method: {method}")

    if len(wave_heights) == 0:
        return {
            "significant_wave_height": 0.0,
            "mean_wave_height": 0.0,
            "max_wave_height": 0.0,
            "rms_wave_height": 0.0,
            "n_waves": 0,
            "mean_period": 0.0,
        }

    # Sort wave heights in descending order
    sorted_heights = np.sort(wave_heights)[::-1]

    # Calculate H1/3 (significant wave height)
    n_third = max(1, len(sorted_heights) // 3)
    h_sig = np.mean(sorted_heights[:n_third])

    # Calculate other statistics
    h_mean = np.mean(wave_heights)
    h_max = np.max(wave_heights)
    h_rms = np.sqrt(np.mean(wave_heights**2))
    t_mean = np.mean(wave_periods) if len(wave_periods) > 0 else 0.0

    return {
        "significant_wave_height": h_sig,
        "mean_wave_height": h_mean,
        "max_wave_height": h_max,
        "rms_wave_height": h_rms,
        "n_waves": len(wave_heights),
        "mean_period": t_mean,
    }


def _zero_crossing_analysis(
    water_levels: np.ndarray, timestep: float
) -> tuple[np.ndarray, np.ndarray]:
    """
    Perform zero-crossing analysis to identify individual waves.

    Parameters
    ----------
    water_levels : np.ndarray
        Water level time series
    timestep : float
        Time step between measurements

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Wave heights and wave periods
    """
    # Remove mean to get fluctuations around zero
    eta = water_levels - np.mean(water_levels)

    # Find zero crossings
    zero_crossings = np.where(np.diff(np.sign(eta)))[0]

    # Separate up-crossings and down-crossings
    up_crossings = []
    down_crossings = []

    for i in zero_crossings:
        if i + 1 < len(eta) and eta[i] < 0 and eta[i + 1] > 0:
            up_crossings.append(i)
        elif i + 1 < len(eta) and eta[i] > 0 and eta[i + 1] < 0:
            down_crossings.append(i)

    # Calculate wave heights and periods
    wave_heights = []
    wave_periods = []

    for i in range(len(up_crossings) - 1):
        # Find corresponding down-crossing
        down_idx = None
        for j, dc in enumerate(down_crossings):
            if up_crossings[i] < dc < up_crossings[i + 1]:
                down_idx = j
                break

        if down_idx is not None:
            # Wave height: difference between max and min in this wave
            start_idx = up_crossings[i]
            end_idx = up_crossings[i + 1]
            wave_segment = water_levels[start_idx:end_idx]

            if len(wave_segment) > 0:
                h_wave = np.max(wave_segment) - np.min(wave_segment)
                wave_heights.append(h_wave)

                # Wave period
                t_wave = (end_idx - start_idx) * timestep
                wave_periods.append(t_wave)

    return np.array(wave_heights), np.array(wave_periods)


def calculate_wave_statistics_for_gauges(
    data: pl.DataFrame, timestep: float
) -> pl.DataFrame:
    """
    Calculate wave statistics for each gauge position.

    Parameters
    ----------
    data : pl.DataFrame
        DataFrame with columns: timestep, water_level, position
    timestep : float
        Time step between measurements

    Returns
    -------
    pl.DataFrame
        DataFrame with wave statistics for each gauge
    """
    results = []

    for position in data["position"].unique().sort():
        gauge_data = data.filter(pl.col("position") == position).sort(
            "timestep"
        )
        water_levels = gauge_data["water_level"].to_numpy()

        stats = calculate_wave_heights(water_levels, timestep)
        stats["position"] = position
        results.append(stats)

    return pl.DataFrame(results)
