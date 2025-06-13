import hashlib
import random
from typing import Any, Dict, Optional
from unittest.mock import Mock, patch

import pytest
import pydantic

from src.utils import validators as validators_utils


# Test models for validation testing
class MockModel(pydantic.BaseModel):
    """Mock model for testing validators."""
    name: str
    value: int
    hash: str = ""
    
    # Apply hash validator
    _hash_config = validators_utils.hash_config()


class MockSubModel(pydantic.BaseModel):
    """Mock sub-model for testing parse_config validator."""
    setting: str = "default"
    number: int = 42


def create_mock_submodel(data=None):
    """Factory function for MockSubModel."""
    if data is None:
        return MockSubModel()
    return MockSubModel(**data)


class MockModelWithSubconfig(pydantic.BaseModel):
    """Mock model with sub-configuration for testing parse_config."""
    title: str
    config: MockSubModel = pydantic.Field(default_factory=MockSubModel)
    hash: str = ""
    
    # Apply validators
    _parse_config = validators_utils.parse_config("config", create_mock_submodel)
    _hash_config = validators_utils.hash_config()


class MockModelWithSeed(pydantic.BaseModel):
    """Mock model for testing seed validation."""
    name: str
    seed: int = 0
    
    # Apply validators
    _set_seed = validators_utils.set_seed_if_missing("seed")


class TestHashConfig:
    def test_hash_config_basic(self) -> None:
        """Test basic hash_config validator functionality."""
        # Create a model instance - hash should be automatically generated
        model = MockModel(name="test", value=123)
        
        # Check that hash was set
        assert len(model.hash) == 8
        assert model.hash != ""

    def test_hash_config_with_ignore_fields(self) -> None:
        """Test hash_config validator with ignored fields."""
        # Create models with ignored fields using a custom model
        class ModelWithIgnore(pydantic.BaseModel):
            name: str
            value: int
            hash: str = ""
            
            _hash_config = validators_utils.hash_config(ignore=["value"])
        
        # Create two models with different values but same name
        model1 = ModelWithIgnore(name="test", value=123)
        model2 = ModelWithIgnore(name="test", value=456)
        
        # They should have the same hash since 'value' is ignored
        assert model1.hash == model2.hash

    def test_hash_config_different_data_different_hash(self) -> None:
        """Test that different data produces different hashes."""
        model1 = MockModel(name="test1", value=123)
        model2 = MockModel(name="test2", value=123)
        
        # Different names should produce different hashes
        assert model1.hash != model2.hash

    def test_hash_config_same_data_same_hash(self) -> None:
        """Test that identical data produces identical hashes."""
        model1 = MockModel(name="test", value=123)
        model2 = MockModel(name="test", value=123)
        
        # Same data should produce same hash
        assert model1.hash == model2.hash

    def test_hash_config_empty_ignore_list(self) -> None:
        """Test hash_config with empty ignore list."""
        class ModelWithEmptyIgnore(pydantic.BaseModel):
            name: str
            value: int
            hash: str = ""
            
            _hash_config = validators_utils.hash_config(ignore=[])
        
        model = ModelWithEmptyIgnore(name="test", value=123)
        assert len(model.hash) == 8

    def test_hash_config_preserves_existing_hash_format(self) -> None:
        """Test that hash_config preserves existing hash format when present."""
        # Model with existing hash in format "hash_suffix"
        model = MockModel(name="test", value=123, hash="abcd1234_suffix")
        
        # Hash should be updated but suffix preserved
        assert "_suffix" in model.hash
        assert len(model.hash.split("_")[0]) == 8

    def test_hash_config_with_complex_ignore_patterns(self) -> None:
        """Test hash_config ignoring multiple fields."""
        class ModelWithMultipleIgnore(pydantic.BaseModel):
            name: str
            value: int
            hash: str = ""
            
            _hash_config = validators_utils.hash_config(ignore=["value", "hash"])
        
        model1 = ModelWithMultipleIgnore(name="test", value=100)
        model2 = ModelWithMultipleIgnore(name="test", value=200)
        
        # Should have same hash since both value and hash are ignored
        assert model1.hash == model2.hash


class TestParseConfig:
    def test_parse_config_with_dict_input(self) -> None:
        """Test parse_config validator with dictionary input."""
        # Test with dict input - should be parsed to MockSubModel
        model = MockModelWithSubconfig(
            title="test",
            config={"setting": "custom", "number": 100}
        )
        
        assert isinstance(model.config, MockSubModel)
        assert model.config.setting == "custom"
        assert model.config.number == 100

    def test_parse_config_with_none_input(self) -> None:
        """Test parse_config validator with None input."""
        # Test with None input - should use default factory
        model = MockModelWithSubconfig(title="test", config=None)
        
        assert isinstance(model.config, MockSubModel)
        assert model.config.setting == "default"
        assert model.config.number == 42

    def test_parse_config_with_model_input(self) -> None:
        """Test parse_config validator with existing model instance."""
        # Test with existing model instance
        existing_model = MockSubModel(setting="existing", number=999)
        model = MockModelWithSubconfig(title="test", config=existing_model)
        
        # Should use the provided instance
        assert model.config is existing_model
        assert model.config.setting == "existing"
        assert model.config.number == 999

    def test_parse_config_function_called_correctly(self) -> None:
        """Test that parse_config calls the provided function correctly."""
        mock_function = Mock(return_value=MockSubModel(setting="mocked", number=123))
        
        class TestModel(pydantic.BaseModel):
            title: str
            config: MockSubModel = pydantic.Field(default_factory=MockSubModel)
            
            _parse_config = validators_utils.parse_config("config", mock_function)
        
        # Test with dict input
        test_data = {"setting": "test", "number": 456}
        model = TestModel(title="test", config=test_data)
        
        # Function should be called with the test data
        mock_function.assert_called_once_with(test_data)
        assert model.config.setting == "mocked"
        assert model.config.number == 123

    def test_parse_config_function_called_with_none(self) -> None:
        """Test that parse_config calls function with no args when input is None."""
        mock_function = Mock(return_value=MockSubModel(setting="default_mock", number=0))
        
        class TestModel(pydantic.BaseModel):
            title: str
            config: MockSubModel = pydantic.Field(default_factory=MockSubModel)
            
            _parse_config = validators_utils.parse_config("config", mock_function)
        
        # Test with None input
        model = TestModel(title="test", config=None)
        
        # Function should be called with no arguments
        mock_function.assert_called_once_with()
        assert model.config.setting == "default_mock"
        assert model.config.number == 0


class TestSetField:
    def test_set_field_basic(self) -> None:
        """Test basic set_field validator functionality."""
        class TestModel(pydantic.BaseModel):
            name: str
            
            _set_name = validators_utils.set_field("name", "forced_value")
        
        # Should use the forced value regardless of input
        model = TestModel(name="original_value")
        assert model.name == "forced_value"

    def test_set_field_ignores_input(self) -> None:
        """Test that set_field ignores the input value."""
        class TestModel(pydantic.BaseModel):
            value: int
            
            _set_value = validators_utils.set_field("value", 999)
        
        # Test with different input values
        assert TestModel(value=123).value == 999
        assert TestModel(value="string").value == 999  # type: ignore
        assert TestModel(value=None).value == 999  # type: ignore

    def test_set_field_with_different_types(self) -> None:
        """Test set_field with different value types."""
        # String value
        class StringModel(pydantic.BaseModel):
            field: str
            _set_field = validators_utils.set_field("field", "test_string")
        
        assert StringModel(field="anything").field == "test_string"
        
        # Integer value
        class IntModel(pydantic.BaseModel):
            field: int
            _set_field = validators_utils.set_field("field", 42)
        
        assert IntModel(field=999).field == 42
        
        # List value
        class ListModel(pydantic.BaseModel):
            field: list
            _set_field = validators_utils.set_field("field", [1, 2, 3])
        
        assert ListModel(field=[]).field == [1, 2, 3]
        
        # Dict value
        class DictModel(pydantic.BaseModel):
            field: dict
            _set_field = validators_utils.set_field("field", {"key": "value"})
        
        assert DictModel(field={}).field == {"key": "value"}

    def test_set_field_with_none_value(self) -> None:
        """Test set_field when the forced value is None."""
        class TestModel(pydantic.BaseModel):
            field: Optional[str]
            _set_field = validators_utils.set_field("field", None)
        
        assert TestModel(field="anything").field is None


class TestSetSeedIfMissing:
    def test_set_seed_if_missing_with_zero(self) -> None:
        """Test set_seed_if_missing when seed is explicitly set to 0."""
        with patch('src.utils.validators.random.randint', return_value=12345):
            model = MockModelWithSeed(name="test", seed=0)  # explicitly set to 0
            assert model.seed == 12345

    def test_set_seed_if_missing_with_nonzero(self) -> None:
        """Test set_seed_if_missing when seed is not 0."""
        # Should return the original value when not 0
        assert MockModelWithSeed(name="test", seed=42).seed == 42
        assert MockModelWithSeed(name="test", seed=1).seed == 1
        assert MockModelWithSeed(name="test", seed=-1).seed == -1
        assert MockModelWithSeed(name="test", seed=999999).seed == 999999

    @patch('src.utils.validators.random.randint')
    def test_set_seed_if_missing_random_range(self, mock_randint: Mock) -> None:
        """Test that set_seed_if_missing uses correct random range."""
        mock_randint.return_value = 50000
        
        MockModelWithSeed(name="test", seed=0)  # explicitly set to 0
        
        # Should call randint with range 0 to 100,000
        mock_randint.assert_called_once_with(0, 100_000)

    def test_set_seed_if_missing_multiple_calls(self) -> None:
        """Test set_seed_if_missing generates different values on multiple calls."""
        # Use non-zero seeds since seed=0 triggers random generation
        seeds = [MockModelWithSeed(name=f"test{i}", seed=i+1).seed for i in range(10)]
        
        # Should keep the original seeds when they're not 0
        expected_seeds = list(range(1, 11))
        assert seeds == expected_seeds
        assert len(set(seeds)) == 10  # All should be different


class TestHashConfigInternal:
    def test_hash_config_internal_basic(self) -> None:
        """Test _hash_config internal function."""
        config = {"name": "test", "value": 123}
        hash_result = validators_utils._hash_config(config)
        
        assert len(hash_result) == 8
        assert isinstance(hash_result, str)

    def test_hash_config_internal_with_prev_hash(self) -> None:
        """Test _hash_config with previous hash."""
        config = {"name": "test", "value": 123}
        prev_hash = "abcd1234_suffix"
        
        hash_result = validators_utils._hash_config(config, prev_hash)
        
        # Should preserve the suffix
        assert hash_result.endswith("_suffix")
        assert len(hash_result.split("_")[0]) == 8

    def test_hash_config_internal_no_prev_hash_suffix(self) -> None:
        """Test _hash_config with previous hash without suffix."""
        config = {"name": "test", "value": 123}
        prev_hash = "abcd1234"  # No suffix
        
        hash_result = validators_utils._hash_config(config, prev_hash)
        
        # Should just return the new hash without suffix
        assert len(hash_result) == 8
        assert "_" not in hash_result

    def test_hash_config_internal_consistent_hashing(self) -> None:
        """Test that _hash_config produces consistent results."""
        config = {"name": "test", "value": 123, "nested": {"key": "value"}}
        
        hash1 = validators_utils._hash_config(config)
        hash2 = validators_utils._hash_config(config)
        
        assert hash1 == hash2

    def test_hash_config_internal_different_configs(self) -> None:
        """Test that different configs produce different hashes."""
        config1 = {"name": "test1", "value": 123}
        config2 = {"name": "test2", "value": 123}
        
        hash1 = validators_utils._hash_config(config1)
        hash2 = validators_utils._hash_config(config2)
        
        assert hash1 != hash2

    @patch('hashlib.sha256')
    def test_hash_config_internal_uses_sha256(self, mock_sha256: Mock) -> None:
        """Test that _hash_config uses SHA256 hashing."""
        mock_hash_obj = Mock()
        mock_hash_obj.hexdigest.return_value = "abcdef1234567890" * 4  # 64 chars
        mock_sha256.return_value = mock_hash_obj
        
        config = {"test": "data"}
        result = validators_utils._hash_config(config)
        
        # Should use SHA256 and take first 8 characters
        mock_sha256.assert_called_once()
        assert result == "abcdef12"


class TestPrepareConfigForHashing:
    def test_prepare_config_dict(self) -> None:
        """Test _prepare_config_for_hashing with dictionary."""
        config = {
            "z_field": "last",
            "a_field": "first", 
            "hash": "should_be_removed",
            "m_field": "middle"
        }
        
        result = validators_utils._prepare_config_for_hashing(config)
        
        # Should remove 'hash' field and sort keys
        expected_keys = ["a_field", "m_field", "z_field"]
        assert list(result.keys()) == expected_keys
        assert "hash" not in result
        assert result["a_field"] == "first"
        assert result["m_field"] == "middle"
        assert result["z_field"] == "last"

    def test_prepare_config_list(self) -> None:
        """Test _prepare_config_for_hashing with list."""
        config = [
            {"name": "first", "hash": "remove1"},
            {"name": "second", "hash": "remove2"},
            "simple_string"
        ]
        
        result = validators_utils._prepare_config_for_hashing(config)
        
        assert len(result) == 3
        assert result[0] == {"name": "first"}  # hash removed
        assert result[1] == {"name": "second"}  # hash removed
        assert result[2] == "simple_string"  # unchanged

    def test_prepare_config_nested_structures(self) -> None:
        """Test _prepare_config_for_hashing with nested structures."""
        config = {
            "level1": {
                "level2": {
                    "value": "deep",
                    "hash": "remove_deep"
                },
                "list": [
                    {"item": 1, "hash": "remove1"},
                    {"item": 2, "hash": "remove2"}
                ],
                "hash": "remove_mid"
            },
            "hash": "remove_top"
        }
        
        result = validators_utils._prepare_config_for_hashing(config)
        
        # Check top level
        assert "hash" not in result
        assert "level1" in result
        
        # Check nested dict
        level1 = result["level1"]
        assert "hash" not in level1
        assert level1["level2"]["value"] == "deep"
        assert "hash" not in level1["level2"]
        
        # Check nested list
        assert len(level1["list"]) == 2
        assert level1["list"][0] == {"item": 1}
        assert level1["list"][1] == {"item": 2}

    def test_prepare_config_primitive_types(self) -> None:
        """Test _prepare_config_for_hashing with primitive types."""
        # String
        assert validators_utils._prepare_config_for_hashing("test") == "test"
        
        # Integer
        assert validators_utils._prepare_config_for_hashing(42) == 42
        
        # Float
        assert validators_utils._prepare_config_for_hashing(3.14) == 3.14
        
        # Boolean
        assert validators_utils._prepare_config_for_hashing(True) is True
        assert validators_utils._prepare_config_for_hashing(False) is False
        
        # None
        assert validators_utils._prepare_config_for_hashing(None) is None

    def test_prepare_config_empty_structures(self) -> None:
        """Test _prepare_config_for_hashing with empty structures."""
        # Empty dict
        assert validators_utils._prepare_config_for_hashing({}) == {}
        
        # Empty list
        assert validators_utils._prepare_config_for_hashing([]) == []
        
        # Dict with only hash field
        result = validators_utils._prepare_config_for_hashing({"hash": "only_hash"})
        assert result == {}

    def test_prepare_config_preserves_order_in_lists(self) -> None:
        """Test that _prepare_config_for_hashing preserves list order."""
        config = [
            {"name": "third", "order": 3},
            {"name": "first", "order": 1}, 
            {"name": "second", "order": 2}
        ]
        
        result = validators_utils._prepare_config_for_hashing(config)
        
        # Order should be preserved in list
        assert result[0]["name"] == "third"
        assert result[1]["name"] == "first"
        assert result[2]["name"] == "second"

    def test_prepare_config_sorts_dict_keys(self) -> None:
        """Test that _prepare_config_for_hashing sorts dictionary keys."""
        config = {
            "zebra": 1,
            "apple": 2,
            "monkey": 3,
            "banana": 4
        }
        
        result = validators_utils._prepare_config_for_hashing(config)
        
        # Keys should be sorted alphabetically
        assert list(result.keys()) == ["apple", "banana", "monkey", "zebra"]


class TestValidatorsIntegration:
    """Integration tests combining multiple validators."""
    
    def test_hash_config_with_parsed_subconfig(self) -> None:
        """Test hash_config working with parse_config results."""
        # MockModelWithSubconfig already has both validators
        model = MockModelWithSubconfig(
            title="test",
            config={"setting": "custom", "number": 999}
        )
        
        # Config should be parsed and hash should be generated
        assert isinstance(model.config, MockSubModel)
        assert model.config.setting == "custom"
        assert model.config.number == 999
        assert len(model.hash) == 8

    def test_set_field_with_hash_config(self) -> None:
        """Test set_field working together with hash_config."""
        class TestModel(pydantic.BaseModel):
            name: str
            fixed_value: str = ""
            hash: str = ""
            
            # Apply validators
            _set_fixed = validators_utils.set_field("fixed_value", "always_this")
            _hash_config = validators_utils.hash_config()
        
        model = TestModel(name="test", fixed_value="user_input")
        
        # Field should be set to fixed value and hash generated
        assert model.fixed_value == "always_this"
        assert len(model.hash) == 8

    def test_seed_validator_integration(self) -> None:
        """Test set_seed_if_missing in a real model context."""
        with patch('src.utils.validators.random.randint', return_value=99999):
            class TestModel(pydantic.BaseModel):
                name: str
                seed: int = 0
                hash: str = ""
                
                # Apply validators
                _set_seed = validators_utils.set_seed_if_missing("seed")
                _hash_config = validators_utils.hash_config()
            
            # Model with explicit seed=0 should get random seed
            model1 = TestModel(name="test1", seed=0)  # explicitly set to 0
            assert model1.seed == 99999
            assert len(model1.hash) == 8
            
            # Model with explicit non-zero seed should keep it
            model2 = TestModel(name="test2", seed=42)
            assert model2.seed == 42
            assert len(model2.hash) == 8
            
            # Model using default value should keep default (validator doesn't run)
            model3 = TestModel(name="test3")  # uses default seed=0
            assert model3.seed == 0
            assert len(model3.hash) == 8

    def test_complex_nested_hashing(self) -> None:
        """Test hashing with complex nested structures."""
        class NestedModel(pydantic.BaseModel):
            data: Dict[str, Any]
            hash: str = ""
            
            _hash_config = validators_utils.hash_config()
        
        complex_data = {
            "level1": {
                "level2": {
                    "values": [1, 2, 3],
                    "settings": {"a": 1, "b": 2}
                }
            },
            "list_of_dicts": [
                {"name": "first", "value": 100},
                {"name": "second", "value": 200}
            ]
        }
        
        model = NestedModel(data=complex_data)
        
        # Hash should be generated consistently
        assert len(model.hash) == 8
        
        # Same data should produce same hash
        model2 = NestedModel(data=complex_data)
        assert model.hash == model2.hash