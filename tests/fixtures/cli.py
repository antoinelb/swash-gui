from pathlib import Path
from typing import Any

import pytest
import typer
from typer.testing import CliRunner

from src import cli


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def cli_app() -> typer.Typer:
    """Get the CLI app."""
    return cli.app


@pytest.fixture
def mock_simulation_runner(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock the SimulationRunner to prevent actual simulations."""
    class MockSimulationRunner:
        def __init__(self):
            pass
        
        def run(self, config: Any, output_dir: Path) -> None:
            # Create minimal output files
            swash_dir = output_dir / "swash"
            swash_dir.mkdir(exist_ok=True, parents=True)
            (swash_dir / "PRINT").write_text("Mock simulation completed")
        
        def analyze(self, config: Any, sim_dir: Path) -> None:
            # Create minimal analysis output
            results_dir = sim_dir / "results"
            results_dir.mkdir(exist_ok=True)
            (results_dir / "analysis.txt").write_text("Mock analysis completed")
    
    monkeypatch.setattr("src.simulation.SimulationRunner", MockSimulationRunner)


@pytest.fixture
def mock_dashboard_server(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock the dashboard server to prevent actual server startup."""
    def mock_run(*args: Any, **kwargs: Any) -> None:
        print("Mock dashboard server started on http://localhost:8000")
    
    monkeypatch.setattr("uvicorn.run", mock_run)