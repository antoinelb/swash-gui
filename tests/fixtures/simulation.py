from pathlib import Path
from unittest.mock import Mock

import pytest

from src import config, simulation


@pytest.fixture
def mock_swash_executable(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock SWASH executable check."""
    mock_which = Mock(return_value="/usr/bin/swash")
    monkeypatch.setattr("shutil.which", mock_which)
    return mock_which


@pytest.fixture
def simulation_directory(tmp_simulations_dir: Path, full_config: config.Config) -> Path:
    """Create a simulation directory."""
    sim_name = f"{full_config.name}_{full_config.hash[:8]}"
    sim_dir = tmp_simulations_dir / sim_name
    sim_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (sim_dir / "swash").mkdir(exist_ok=True)
    (sim_dir / "results").mkdir(exist_ok=True)
    
    return sim_dir


@pytest.fixture
def input_template(tmp_templates_dir: Path) -> Path:
    """Create a minimal INPUT template."""
    template_content = """PROJECT 'test' 'test_run'
SET level={{ water.water_level }}

MODE DYN

CGRID CURV 0 0 0 {{ grid.length }} 0 {{ grid.nx_cells }} 0 0

INPGRID BOT CURV 0 0 0 {{ grid.nx_cells }} 0 {{ grid.length }} 0

{% if breakwater.enable %}
INPGRID PORO CURV 0 0 0 {{ grid.nx_cells }} 0 {{ grid.length }} 0
{% endif %}

{% if vegetation.enable %}
INPGRID VEG CURV 0 0 0 {{ grid.nx_cells }} 0 {{ grid.length }} 0
{% endif %}

BOUND SHAP JON
BOU SIDE W CCW CON REG {{ water.wave_height }} {{ water.wave_period }} 0

PHYSICS VISC KEPS

COMPUTE

STOP
"""
    template_path = tmp_templates_dir / "INPUT"
    template_path.write_text(template_content)
    return template_path


@pytest.fixture
def bathymetry_data() -> str:
    """Sample bathymetry data."""
    return "\n".join([f"{x}\t{-0.02 * x}" for x in range(0, 112)])


@pytest.fixture
def mock_run_simulation(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock the run_simulation function."""
    mock_run = Mock()
    monkeypatch.setattr("src.simulation.run_simulation", mock_run)
    return mock_run


@pytest.fixture
def completed_simulation_dir(simulation_directory: Path) -> Path:
    """Create a simulation directory with output files."""
    swash_dir = simulation_directory / "swash"
    
    # Create fake output files
    (swash_dir / "test_run.tab").write_text("TIME\tHSIG\n0\t0.1\n1\t0.09\n")
    (swash_dir / "test_run.mat").write_bytes(b"fake matlab data")
    (swash_dir / "PRINT").write_text("Simulation completed successfully")
    
    return simulation_directory