from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def test_root() -> Path:
    """Root directory for tests."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def fixtures_dir(test_root: Path) -> Path:
    """Directory containing test fixtures."""
    return test_root / "fixtures"


@pytest.fixture(scope="session")
def test_data_dir(fixtures_dir: Path) -> Path:
    """Directory containing test data files."""
    return fixtures_dir / "data"


@pytest.fixture
def tmp_config_dir(tmp_path: Path) -> Path:
    """Temporary directory for config files."""
    config_dir = tmp_path / "config"
    config_dir.mkdir(exist_ok=True)
    return config_dir


@pytest.fixture
def tmp_simulations_dir(tmp_path: Path) -> Path:
    """Temporary directory for simulations."""
    sim_dir = tmp_path / "simulations"
    sim_dir.mkdir(exist_ok=True)
    return sim_dir


@pytest.fixture
def tmp_templates_dir(tmp_path: Path) -> Path:
    """Temporary directory for templates."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir(exist_ok=True)
    return templates_dir