import json
import pytest
from pathlib import Path
from unittest.mock import patch, Mock, mock_open
from starlette.applications import Starlette
from starlette.testclient import TestClient
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.dashboard.api import routes
from src import config as config_module


@pytest.fixture
def api_client():
    """Create test client for API routes."""
    app = Starlette(routes=routes.get_api_routes())
    return TestClient(app)


@pytest.fixture
def mock_config():
    """Mock config object."""
    cfg = Mock()
    cfg.name = "test_config"
    cfg.hash = "abcd1234567890"
    cfg.grid.model_dump.return_value = {"x_start": 0, "x_end": 100}
    cfg.water.model_dump.return_value = {"water_level": 1.0, "wave_height": 0.1}
    cfg.breakwater.model_dump.return_value = {"enable": True}
    cfg.vegetation.model_dump.return_value = {"enable": False}
    cfg.numeric.model_dump.return_value = {"time_step": 0.01}
    return cfg


@pytest.fixture
def mock_config_dir(tmp_path):
    """Create temporary config directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Patch the CONFIG_DIR constant
    with patch('src.dashboard.api.routes.CONFIG_DIR', config_dir):
        yield config_dir


class TestListConfigs:
    """Test cases for list_configs endpoint."""

    @patch('src.dashboard.api.routes.CONFIG_DIR')
    def test_list_configs_no_directory(self, mock_config_dir):
        """Test listing configs when directory doesn't exist."""
        mock_config_dir.exists.return_value = False
        
        request = Mock(spec=Request)
        import asyncio
        response = asyncio.run(routes.list_configs(request))
        
        assert response.body == b'{"configs":[]}'

    def test_list_configs_empty_directory(self, api_client, mock_config_dir):
        """Test listing configs with empty directory."""
        response = api_client.get("/configs")
        assert response.status_code == 200
        assert response.json() == {"configs": []}

    def test_list_configs_with_valid_configs(self, api_client, mock_config_dir, mock_config):
        """Test listing configs with valid configuration files."""
        # Create mock config file
        config_file = mock_config_dir / "test1.yml"
        config_file.write_text("name: test1")
        
        with patch('src.dashboard.api.routes.config_module.read_config', return_value=mock_config):
            response = api_client.get("/configs")
            
        assert response.status_code == 200
        data = response.json()
        assert len(data["configs"]) == 1
        assert data["configs"][0]["name"] == "test_config"
        assert data["configs"][0]["hash"] == "abcd1234"

    def test_list_configs_with_invalid_config(self, api_client, mock_config_dir, capsys):
        """Test listing configs with invalid configuration file."""
        # Create invalid config file
        config_file = mock_config_dir / "invalid.yml"
        config_file.write_text("invalid: yaml: content")
        
        with patch('src.dashboard.api.routes.config_module.read_config', 
                  side_effect=Exception("Invalid config")):
            response = api_client.get("/configs")
            
        assert response.status_code == 200
        assert response.json() == {"configs": []}
        
        # Check that error was printed
        captured = capsys.readouterr()
        assert "Error loading config" in captured.out


class TestGetConfig:
    """Test cases for get_config endpoint."""

    def test_get_config_not_found(self, api_client, mock_config_dir):
        """Test getting non-existent config."""
        response = api_client.get("/configs/nonexistent")
        assert response.status_code == 404
        assert "Configuration not found" in response.json()["error"]

    def test_get_config_success(self, api_client, mock_config_dir, mock_config):
        """Test successfully getting a config."""
        config_file = mock_config_dir / "test.yml"
        config_file.write_text("name: test")
        
        with patch('src.dashboard.api.routes.config_module.read_config', return_value=mock_config), \
             patch('src.dashboard.api.routes.compute_wavelength', return_value=10.5):
            response = api_client.get("/configs/test")
            
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test_config"
        assert data["hash"] == "abcd1234567890"
        assert "wavelength" in data["water"]

    def test_get_config_error(self, api_client, mock_config_dir, capsys):
        """Test error handling in get_config."""
        config_file = mock_config_dir / "test.yml"
        config_file.write_text("name: test")
        
        with patch('src.dashboard.api.routes.config_module.read_config', 
                  side_effect=Exception("Config error")):
            response = api_client.get("/configs/test")
            
        assert response.status_code == 500
        assert "Config error" in response.json()["error"]
        
        captured = capsys.readouterr()
        assert "Error getting config test" in captured.out


class TestCreateConfig:
    """Test cases for create_config endpoint."""

    def test_create_config_success(self, api_client, mock_config_dir, mock_config):
        """Test successfully creating a config."""
        config_data = {"name": "new_config", "grid": {}, "water": {}}
        
        with patch('src.dashboard.api.routes.config_module.Config', return_value=mock_config), \
             patch('src.dashboard.api.routes.config_module.write_config') as mock_write:
            response = api_client.post("/configs", json=config_data)
            
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test_config"
        assert data["hash"] == "abcd1234567890"
        mock_write.assert_called_once()

    def test_create_config_error(self, api_client, mock_config_dir, capsys):
        """Test error handling in create_config."""
        config_data = {"invalid": "data"}
        
        with patch('src.dashboard.api.routes.config_module.Config', 
                  side_effect=Exception("Validation error")):
            response = api_client.post("/configs", json=config_data)
            
        assert response.status_code == 400
        assert "Validation error" in response.json()["error"]
        
        captured = capsys.readouterr()
        assert "Error creating config" in captured.out


class TestUpdateConfig:
    """Test cases for update_config endpoint."""

    def test_update_config_not_found(self, api_client, mock_config_dir):
        """Test updating non-existent config."""
        response = api_client.put("/configs/nonexistent", json={"name": "test"})
        assert response.status_code == 404
        assert "Configuration not found" in response.json()["error"]

    def test_update_config_success_same_name(self, api_client, mock_config_dir, mock_config):
        """Test successfully updating config with same name."""
        config_file = mock_config_dir / "test.yml"
        config_file.write_text("name: test")
        
        config_data = {"name": "test", "water": {"water_level": 2.0}}
        
        with patch('src.dashboard.api.routes.config_module.Config', return_value=mock_config), \
             patch('src.dashboard.api.routes.config_module.write_config') as mock_write:
            response = api_client.put("/configs/test", json=config_data)
            
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test_config"
        mock_write.assert_called_once()

    def test_update_config_success_name_change(self, api_client, mock_config_dir, mock_config):
        """Test successfully updating config with name change."""
        config_file = mock_config_dir / "old_name.yml"
        config_file.write_text("name: old_name")
        
        # Mock config with new name
        mock_config.name = "new_name"
        config_data = {"name": "new_name", "water": {"water_level": 2.0}}
        
        with patch('src.dashboard.api.routes.config_module.Config', return_value=mock_config), \
             patch('src.dashboard.api.routes.config_module.write_config') as mock_write:
            response = api_client.put("/configs/old_name", json=config_data)
            
        assert response.status_code == 200
        assert not config_file.exists()  # Old file should be deleted
        mock_write.assert_called_once()

    def test_update_config_error(self, api_client, mock_config_dir, capsys):
        """Test error handling in update_config."""
        config_file = mock_config_dir / "test.yml"
        config_file.write_text("name: test")
        
        with patch('src.dashboard.api.routes.config_module.Config', 
                  side_effect=Exception("Update error")):
            response = api_client.put("/configs/test", json={"name": "test"})
            
        assert response.status_code == 400
        assert "Update error" in response.json()["error"]
        
        captured = capsys.readouterr()
        assert "Error updating config test" in captured.out


class TestDeleteConfig:
    """Test cases for delete_config endpoint."""

    def test_delete_config_not_found(self, api_client, mock_config_dir):
        """Test deleting non-existent config."""
        response = api_client.delete("/configs/nonexistent")
        assert response.status_code == 404
        assert "Configuration not found" in response.json()["error"]

    def test_delete_config_success(self, api_client, mock_config_dir):
        """Test successfully deleting a config."""
        config_file = mock_config_dir / "test.yml"
        config_file.write_text("name: test")
        
        response = api_client.delete("/configs/test")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Configuration deleted"
        assert not config_file.exists()

    def test_delete_config_error(self, api_client, mock_config_dir, capsys):
        """Test error handling in delete_config."""
        config_file = mock_config_dir / "test.yml"
        config_file.write_text("name: test")
        
        # Mock file deletion error
        with patch.object(Path, 'unlink', side_effect=OSError("Permission denied")):
            response = api_client.delete("/configs/test")
            
        assert response.status_code == 500
        assert "Permission denied" in response.json()["error"]
        
        captured = capsys.readouterr()
        assert "Error deleting config test" in captured.out


class TestSimulateConfig:
    """Test cases for simulate_config endpoint."""

    def test_simulate_config_not_found(self, api_client, mock_config_dir):
        """Test simulating non-existent config."""
        response = api_client.post("/simulate/nonexistent")
        assert response.status_code == 404
        assert "Configuration not found" in response.json()["error"]

    def test_simulate_config_success(self, api_client, mock_config_dir, mock_config):
        """Test successfully simulating a config."""
        config_file = mock_config_dir / "test.yml"
        config_file.write_text("name: test")
        
        with patch('src.dashboard.api.routes.config_module.read_config', return_value=mock_config), \
             patch('src.dashboard.api.routes.run_simulation') as mock_run:
            response = api_client.post("/simulate/test")
            
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Simulation completed successfully" in data["message"]
        mock_run.assert_called_once_with(mock_config)

    def test_simulate_config_error(self, api_client, mock_config_dir, mock_config, capsys):
        """Test error handling in simulate_config."""
        config_file = mock_config_dir / "test.yml"
        config_file.write_text("name: test")
        
        with patch('src.dashboard.api.routes.config_module.read_config', return_value=mock_config), \
             patch('src.dashboard.api.routes.run_simulation', 
                   side_effect=Exception("Simulation failed")):
            response = api_client.post("/simulate/test")
            
        assert response.status_code == 500
        assert "Simulation failed" in response.json()["error"]
        
        captured = capsys.readouterr()
        assert "Error running simulation for test" in captured.out


class TestCalculateWavelength:
    """Test cases for calculate_wavelength endpoint."""

    def test_calculate_wavelength_success(self, api_client):
        """Test successfully calculating wavelength."""
        data = {"wave_period": 5.0, "water_level": 2.0}
        
        with patch('src.dashboard.api.routes.compute_wavelength', return_value=25.5):
            response = api_client.post("/wavelength", json=data)
            
        assert response.status_code == 200
        assert response.json()["wavelength"] == 25.5

    def test_calculate_wavelength_missing_params(self, api_client):
        """Test calculating wavelength with missing parameters."""
        data = {"wave_period": 5.0}  # Missing water_level
        
        response = api_client.post("/wavelength", json=data)
        
        assert response.status_code == 400
        assert "wave_period and water_level are required" in response.json()["error"]

    def test_calculate_wavelength_error(self, api_client, capsys):
        """Test error handling in calculate_wavelength."""
        data = {"wave_period": 5.0, "water_level": 2.0}
        
        with patch('src.dashboard.api.routes.compute_wavelength', 
                  side_effect=Exception("Calculation error")):
            response = api_client.post("/wavelength", json=data)
            
        assert response.status_code == 400
        assert "Calculation error" in response.json()["error"]
        
        captured = capsys.readouterr()
        assert "Error calculating wavelength" in captured.out


class TestGetAnalysisResults:
    """Test cases for get_analysis_results endpoint."""

    def test_get_analysis_results_config_not_found(self, api_client, mock_config_dir):
        """Test getting analysis results for non-existent config."""
        response = api_client.get("/analysis/nonexistent")
        assert response.status_code == 404
        assert "Configuration not found" in response.json()["error"]

    def test_get_analysis_results_no_results(self, api_client, mock_config_dir, mock_config):
        """Test getting analysis results when results don't exist."""
        config_file = mock_config_dir / "test.yml"
        config_file.write_text("name: test")
        
        with patch('src.dashboard.api.routes.config_module.read_config', return_value=mock_config), \
             patch('src.dashboard.api.routes.root_dir', mock_config_dir):
            response = api_client.get("/analysis/test")
            
        assert response.status_code == 404
        assert "Analysis results not found" in response.json()["error"]

    def test_get_analysis_results_success_plot_only(self, api_client, mock_config_dir, mock_config):
        """Test successfully getting analysis results with plot data only."""
        config_file = mock_config_dir / "test.yml"
        config_file.write_text("name: test")
        
        # Create mock analysis directory structure
        sim_dir = mock_config_dir / "simulations" / f"{mock_config.name}_{mock_config.hash}"
        analysis_dir = sim_dir / "analysis"
        analysis_dir.mkdir(parents=True)
        
        plot_file = analysis_dir / "water_levels_and_x_velocity.json"
        plot_data = {"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}
        plot_file.write_text(json.dumps(plot_data))
        
        with patch('src.dashboard.api.routes.config_module.read_config', return_value=mock_config), \
             patch('src.dashboard.api.routes.root_dir', mock_config_dir):
            response = api_client.get("/analysis/test")
            
        assert response.status_code == 200
        data = response.json()
        assert data["plot_data"] == plot_data
        assert data["wave_stats"] is None

    def test_get_analysis_results_success_with_wave_stats(self, api_client, mock_config_dir, mock_config):
        """Test successfully getting analysis results with wave statistics."""
        config_file = mock_config_dir / "test.yml"
        config_file.write_text("name: test")
        
        # Create mock analysis directory structure
        sim_dir = mock_config_dir / "simulations" / f"{mock_config.name}_{mock_config.hash}"
        analysis_dir = sim_dir / "analysis"
        analysis_dir.mkdir(parents=True)
        
        plot_file = analysis_dir / "water_levels_and_x_velocity.json"
        plot_data = {"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}
        plot_file.write_text(json.dumps(plot_data))
        
        wave_stats_file = analysis_dir / "wave_statistics.csv"
        wave_stats_file.write_text("gauge,height,period\n1,0.1,2.5\n2,0.2,2.4")
        
        mock_wave_stats = [{"gauge": 1, "height": 0.1, "period": 2.5}]
        
        with patch('src.dashboard.api.routes.config_module.read_config', return_value=mock_config), \
             patch('src.dashboard.api.routes.root_dir', mock_config_dir), \
             patch('polars.read_csv') as mock_read_csv:
            
            mock_df = Mock()
            mock_df.to_dicts.return_value = mock_wave_stats
            mock_read_csv.return_value = mock_df
            
            response = api_client.get("/analysis/test")
            
        assert response.status_code == 200
        data = response.json()
        assert data["plot_data"] == plot_data
        assert data["wave_stats"] == mock_wave_stats

    def test_get_analysis_results_error(self, api_client, mock_config_dir, mock_config, capsys):
        """Test error handling in get_analysis_results."""
        config_file = mock_config_dir / "test.yml"
        config_file.write_text("name: test")
        
        with patch('src.dashboard.api.routes.config_module.read_config', 
                  side_effect=Exception("Analysis error")):
            response = api_client.get("/analysis/test")
            
        assert response.status_code == 500
        assert "Analysis error" in response.json()["error"]
        
        captured = capsys.readouterr()
        assert "Error getting analysis results for test" in captured.out


class TestGetApiRoutes:
    """Test cases for get_api_routes function."""

    def test_get_api_routes_returns_correct_routes(self):
        """Test that get_api_routes returns all expected routes."""
        routes_list = routes.get_api_routes()
        
        # Check that we have the expected number of routes
        assert len(routes_list) == 8
        
        # Check that all expected routes are present
        route_patterns = [route.path for route in routes_list]
        expected_patterns = [
            "/configs",
            "/configs",
            "/configs/{name}",
            "/configs/{name}",
            "/configs/{name}",
            "/simulate/{name}",
            "/analysis/{name}",
            "/wavelength"
        ]
        
        for pattern in expected_patterns:
            assert pattern in route_patterns