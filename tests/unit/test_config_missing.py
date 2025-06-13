"""Tests for missing config.py branch coverage."""

import pytest
from unittest.mock import Mock, patch
import ruamel.yaml

from src import config


class TestConfigMissingBranch:
    """Test cases to cover missing branch in config.py."""

    def test_add_field_comments_missing_field_or_description(self) -> None:
        """Test _add_field_comments when field is missing or has no description (line 282 branch)."""
        # Create a mock config object with fields
        mock_config = Mock()
        
        # Create mock field info with and without descriptions
        field_with_description = Mock()
        field_with_description.description = "This field has a description"
        
        field_without_description = Mock()
        field_without_description.description = None  # No description
        
        # Set up model_fields
        mock_config.__class__.model_fields = {
            "field_with_desc": field_with_description,
            "field_without_desc": field_without_description,
            "missing_field": field_with_description,  # This field won't be in commented_map
        }
        
        # Create commented map with only some fields
        commented_map = ruamel.yaml.CommentedMap()
        commented_map["field_with_desc"] = "value1"
        commented_map["field_without_desc"] = "value2"
        # Note: "missing_field" is intentionally not in the commented_map
        
        # Mock yaml_add_eol_comment method
        commented_map.yaml_add_eol_comment = Mock()
        
        # Call the function
        config._add_field_comments(mock_config, commented_map)
        
        # Verify that comment is only added for field_with_desc
        # (field_without_desc has no description, missing_field is not in map)
        commented_map.yaml_add_eol_comment.assert_called_once_with(
            "This field has a description", "field_with_desc"
        )

    def test_add_field_comments_field_not_in_map(self) -> None:
        """Test _add_field_comments when field exists but not in commented_map."""
        mock_config = Mock()
        
        # Create field with description
        field_info = Mock()
        field_info.description = "Field description"
        
        mock_config.__class__.model_fields = {
            "existing_field": field_info,
        }
        
        # Create empty commented map (field not present)
        commented_map = ruamel.yaml.CommentedMap()
        commented_map.yaml_add_eol_comment = Mock()
        
        # Call the function
        config._add_field_comments(mock_config, commented_map)
        
        # No comment should be added since field is not in the map
        commented_map.yaml_add_eol_comment.assert_not_called()

    def test_add_field_comments_empty_description(self) -> None:
        """Test _add_field_comments when field has empty description."""
        mock_config = Mock()
        
        # Create field with empty description
        field_info = Mock()
        field_info.description = ""  # Empty description
        
        mock_config.__class__.model_fields = {
            "field_name": field_info,
        }
        
        # Create commented map with the field
        commented_map = ruamel.yaml.CommentedMap()
        commented_map["field_name"] = "value"
        commented_map.yaml_add_eol_comment = Mock()
        
        # Call the function
        config._add_field_comments(mock_config, commented_map)
        
        # No comment should be added since description is empty (falsy)
        commented_map.yaml_add_eol_comment.assert_not_called()

    def test_add_field_comments_successful_case(self) -> None:
        """Test _add_field_comments successful case for comparison."""
        mock_config = Mock()
        
        # Create field with description
        field_info = Mock()
        field_info.description = "Valid description"
        
        mock_config.__class__.model_fields = {
            "valid_field": field_info,
        }
        
        # Create commented map with the field
        commented_map = ruamel.yaml.CommentedMap()
        commented_map["valid_field"] = "value"
        commented_map.yaml_add_eol_comment = Mock()
        
        # Call the function
        config._add_field_comments(mock_config, commented_map)
        
        # Comment should be added
        commented_map.yaml_add_eol_comment.assert_called_once_with(
            "Valid description", "valid_field"
        )