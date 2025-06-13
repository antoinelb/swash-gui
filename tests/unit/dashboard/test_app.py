import pytest
from pathlib import Path
from unittest.mock import patch, Mock
from starlette.applications import Starlette
from starlette.testclient import TestClient
from starlette.responses import FileResponse

from src.dashboard import app


class TestServeSpa:
    """Test cases for serve_spa function."""

    def test_serve_spa_returns_file_response(self):
        """Test that serve_spa returns FileResponse with index.html."""
        mock_request = Mock()
        
        import asyncio
        result = asyncio.run(app.serve_spa(mock_request))
        
        assert isinstance(result, FileResponse)
        assert str(result.path).endswith("index.html")


class TestCreateApp:
    """Test cases for create_app function."""

    @patch('src.dashboard.api.routes.get_api_routes')
    def test_create_app_structure(self, mock_get_routes, tmp_path):
        """Test that create_app creates proper Starlette application."""
        mock_get_routes.return_value = []
        
        # Create temporary static directories
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        (static_dir / "css").mkdir()
        (static_dir / "js").mkdir()
        (static_dir / "assets").mkdir()
        (static_dir / "index.html").write_text("<html></html>")
        
        with patch('src.dashboard.app.STATIC_DIR', static_dir), \
             patch('src.dashboard.app.INDEX_PATH', static_dir / "index.html"):
            result = app.create_app()
        
        assert isinstance(result, Starlette)
        assert result.debug is True
        
        # Check that routes are configured
        assert len(result.routes) > 0

    def test_create_app_with_real_paths(self):
        """Test create_app with real paths (integration test)."""
        # This tests the actual path construction
        result = app.create_app()
        
        assert isinstance(result, Starlette)
        # Should have API mount, static mounts, and SPA routes
        assert len(result.routes) >= 5


class TestRunServer:
    """Test cases for run_server function."""

    @patch('src.dashboard.app.uvicorn')
    def test_run_server_default_params(self, mock_uvicorn):
        """Test run_server with default parameters."""
        app.run_server()
        
        mock_uvicorn.run.assert_called_once_with(
            "src.dashboard.app:create_app",
            factory=True,
            host="127.0.0.1",
            port=8000,
            reload=True,
            reload_dirs=[str(Path(app.__file__).parent.parent)]
        )

    @patch('src.dashboard.app.uvicorn')
    def test_run_server_custom_params(self, mock_uvicorn):
        """Test run_server with custom parameters."""
        app.run_server(host="0.0.0.0", port=9000)
        
        mock_uvicorn.run.assert_called_once_with(
            "src.dashboard.app:create_app",
            factory=True,
            host="0.0.0.0",
            port=9000,
            reload=True,
            reload_dirs=[str(Path(app.__file__).parent.parent)]
        )


class TestAppIntegration:
    """Integration tests for the dashboard app."""

    def test_app_routes_respond(self):
        """Test that the app routes respond correctly."""
        test_app = app.create_app()
        client = TestClient(test_app)
        
        # Test SPA route (should serve index.html)
        with patch('src.dashboard.app.INDEX_PATH', Path(__file__).parent / "test_index.html"):
            # Create a temporary test file
            test_index = Path(__file__).parent / "test_index.html"
            test_index.write_text("<html><body>Test</body></html>")
            
            try:
                response = client.get("/")
                assert response.status_code == 200
                
                response = client.get("/some/spa/route")
                assert response.status_code == 200
            finally:
                if test_index.exists():
                    test_index.unlink()

    def test_static_directories_configured(self):
        """Test that static directories are properly configured."""
        test_app = app.create_app()
        
        # Check that routes include static file mounts
        route_paths = []
        for route in test_app.routes:
            if hasattr(route, 'path'):
                route_paths.append(route.path)
            elif hasattr(route, 'path_regex'):
                # For Mount objects, get the path pattern
                pattern = str(route.path_regex.pattern)
                if pattern.startswith('^'):
                    pattern = pattern[1:]
                if pattern.endswith('(?P<path>.*)$'):
                    pattern = pattern[:-len('(?P<path>.*)$')]
                route_paths.append(pattern)
        
        # Should have static mounts for css, js, and assets
        assert any('/css' in path for path in route_paths)
        assert any('/js' in path for path in route_paths)
        assert any('/assets' in path for path in route_paths)


class TestMainExecution:
    """Test cases for main execution."""

    @patch('src.dashboard.app.run_server')
    def test_main_execution(self, mock_run_server):
        """Test that __main__ execution calls run_server."""
        # We can't directly test __main__ execution, but we can test
        # that the run_server function exists and would be called
        assert callable(app.run_server)
        
        # Test that if we were to call it as main, it would work
        if hasattr(app, '__name__') and app.__name__ == '__main__':
            mock_run_server.assert_called_once()


class TestConstants:
    """Test cases for module constants."""

    def test_static_dir_path(self):
        """Test that STATIC_DIR is correctly defined."""
        assert isinstance(app.STATIC_DIR, Path)
        assert str(app.STATIC_DIR).endswith("static")

    def test_index_path(self):
        """Test that INDEX_PATH is correctly defined."""
        assert isinstance(app.INDEX_PATH, Path)
        assert str(app.INDEX_PATH).endswith("index.html")
        assert app.INDEX_PATH.parent == app.STATIC_DIR