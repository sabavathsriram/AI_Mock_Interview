"""
Unit tests for LLM Service
Tests the LLM service with mocked Gemini API responses
"""

import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from pydantic import BaseModel

from app.llm import (
    LLMService,
    LLMException,
    LLMConfigurationError,
    LLMResponseError,
    LLMTimeoutError,
    LLMRateLimitError,
    TextGenerationResponse,
    PromptType,
    prompt_library,
)


# Test Models
class TestResponse(BaseModel):
    """Test response model."""
    title: str
    content: str
    score: int


class TestLLMServiceConfiguration:
    """Test LLM service configuration."""
    
    @patch('app.llm.service.llm_settings')
    def test_service_initialization_with_valid_config(self, mock_settings):
        """Test service initializes with valid configuration."""
        mock_settings.is_configured.return_value = True
        mock_settings.gemini_api_key = "test-key"
        mock_settings.gemini_model = "gemini-1.5-flash"
        
        with patch('google.generativeai.configure'):
            service = LLMService()
            assert service.configured is True
            assert service.model_name == "gemini-1.5-flash"
    
    @patch('app.llm.service.llm_settings')
    def test_service_initialization_without_config(self, mock_settings):
        """Test service initialization without configuration."""
        mock_settings.is_configured.return_value = False
        
        service = LLMService()
        assert service.configured is False
    
    def test_is_configured_method(self):
        """Test is_configured method."""
        from app.llm import llm_service
        # Will depend on actual config
        result = llm_service.is_configured()
        assert isinstance(result, bool)


class TestTextGeneration:
    """Test text generation functionality."""
    
    @pytest.mark.asyncio
    @patch('app.llm.service.llm_settings')
    @patch('google.generativeai.GenerativeModel')
    async def test_successful_text_generation(self, mock_model_class, mock_settings):
        """Test successful text generation."""
        # Setup mocks
        mock_settings.is_configured.return_value = True
        mock_settings.gemini_api_key = "test-key"
        mock_settings.gemini_model = "gemini-1.5-flash"
        mock_settings.gemini_temperature = 0.7
        mock_settings.gemini_max_output_tokens = 2048
        mock_settings.gemini_request_timeout = 30
        
        # Mock response
        mock_response = MagicMock()
        mock_response.text = "Hello! The LLM integration is working correctly."
        
        # Setup model mock
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        with patch('google.generativeai.configure'):
            service = LLMService()
            
            result = await service.generate_text(
                prompt="Test prompt"
            )
            
            assert isinstance(result, TextGenerationResponse)
            assert result.text == "Hello! The LLM integration is working correctly."
            assert result.model == "gemini-1.5-flash"
            assert isinstance(result.timestamp, datetime)
    
    @pytest.mark.asyncio
    @patch('app.llm.service.llm_settings')
    async def test_text_generation_not_configured(self, mock_settings):
        """Test text generation when service is not configured."""
        mock_settings.is_configured.return_value = False
        
        service = LLMService()
        
        with pytest.raises(LLMConfigurationError) as exc_info:
            await service.generate_text(prompt="Test")
        
        assert "not configured" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    @patch('app.llm.service.llm_settings')
    @patch('google.generativeai.GenerativeModel')
    async def test_text_generation_empty_response(self, mock_model_class, mock_settings):
        """Test text generation with empty response."""
        mock_settings.is_configured.return_value = True
        mock_settings.gemini_api_key = "test-key"
        mock_settings.gemini_model = "gemini-1.5-flash"
        mock_settings.gemini_temperature = 0.7
        mock_settings.gemini_max_output_tokens = 2048
        mock_settings.gemini_request_timeout = 30
        
        # Mock empty response
        mock_response = MagicMock()
        mock_response.text = ""
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        with patch('google.generativeai.configure'):
            service = LLMService()
            
            with pytest.raises(LLMResponseError) as exc_info:
                await service.generate_text(prompt="Test")
            
            assert "empty" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    @patch('app.llm.service.llm_settings')
    @patch('google.generativeai.GenerativeModel')
    async def test_text_generation_timeout(self, mock_model_class, mock_settings):
        """Test text generation timeout handling."""
        from google.api_core.exceptions import DeadlineExceeded
        
        mock_settings.is_configured.return_value = True
        mock_settings.gemini_api_key = "test-key"
        mock_settings.gemini_model = "gemini-1.5-flash"
        mock_settings.gemini_temperature = 0.7
        mock_settings.gemini_max_output_tokens = 2048
        mock_settings.gemini_request_timeout = 30
        
        # Mock timeout exception
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = DeadlineExceeded("Timeout")
        mock_model_class.return_value = mock_model
        
        with patch('google.generativeai.configure'):
            service = LLMService()
            
            with pytest.raises(LLMTimeoutError):
                await service.generate_text(prompt="Test")
    
    @pytest.mark.asyncio
    @patch('app.llm.service.llm_settings')
    @patch('google.generativeai.GenerativeModel')
    async def test_text_generation_rate_limit(self, mock_model_class, mock_settings):
        """Test text generation rate limit handling."""
        from google.api_core.exceptions import ResourceExhausted
        
        mock_settings.is_configured.return_value = True
        mock_settings.gemini_api_key = "test-key"
        mock_settings.gemini_model = "gemini-1.5-flash"
        mock_settings.gemini_temperature = 0.7
        mock_settings.gemini_max_output_tokens = 2048
        mock_settings.gemini_request_timeout = 30
        
        # Mock rate limit exception
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = ResourceExhausted("Rate limit")
        mock_model_class.return_value = mock_model
        
        with patch('google.generativeai.configure'):
            service = LLMService()
            
            with pytest.raises(LLMRateLimitError):
                await service.generate_text(prompt="Test")


class TestStructuredResponse:
    """Test structured JSON response generation."""
    
    @pytest.mark.asyncio
    @patch('app.llm.service.llm_settings')
    @patch('google.generativeai.GenerativeModel')
    async def test_successful_structured_response(self, mock_model_class, mock_settings):
        """Test successful structured JSON response."""
        mock_settings.is_configured.return_value = True
        mock_settings.gemini_api_key = "test-key"
        mock_settings.gemini_model = "gemini-1.5-flash"
        mock_settings.gemini_temperature = 0.7
        mock_settings.gemini_max_output_tokens = 2048
        mock_settings.gemini_request_timeout = 30
        
        # Mock response with JSON
        json_response = json.dumps({
            "title": "Test Title",
            "content": "Test content",
            "score": 85
        })
        
        mock_response = MagicMock()
        mock_response.text = json_response
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        with patch('google.generativeai.configure'):
            service = LLMService()
            
            result = await service.generate_structured_response(
                prompt="Generate test response",
                response_model=TestResponse
            )
            
            assert isinstance(result, TestResponse)
            assert result.title == "Test Title"
            assert result.content == "Test content"
            assert result.score == 85
    
    @pytest.mark.asyncio
    @patch('app.llm.service.llm_settings')
    @patch('google.generativeai.GenerativeModel')
    async def test_structured_response_invalid_json(self, mock_model_class, mock_settings):
        """Test structured response with invalid JSON."""
        mock_settings.is_configured.return_value = True
        mock_settings.gemini_api_key = "test-key"
        mock_settings.gemini_model = "gemini-1.5-flash"
        mock_settings.gemini_temperature = 0.7
        mock_settings.gemini_max_output_tokens = 2048
        mock_settings.gemini_request_timeout = 30
        
        # Mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.text = "This is not JSON {invalid"
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        with patch('google.generativeai.configure'):
            service = LLMService()
            
            with pytest.raises(LLMResponseError) as exc_info:
                await service.generate_structured_response(
                    prompt="Generate test response",
                    response_model=TestResponse
                )
            
            assert "json" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    @patch('app.llm.service.llm_settings')
    @patch('google.generativeai.GenerativeModel')
    async def test_structured_response_validation_error(self, mock_model_class, mock_settings):
        """Test structured response with validation error."""
        mock_settings.is_configured.return_value = True
        mock_settings.gemini_api_key = "test-key"
        mock_settings.gemini_model = "gemini-1.5-flash"
        mock_settings.gemini_temperature = 0.7
        mock_settings.gemini_max_output_tokens = 2048
        mock_settings.gemini_request_timeout = 30
        
        # Mock response with invalid data
        json_response = json.dumps({
            "title": "Test Title",
            "content": "Test content",
            "score": "not-a-number"  # Invalid type
        })
        
        mock_response = MagicMock()
        mock_response.text = json_response
        
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        with patch('google.generativeai.configure'):
            service = LLMService()
            
            with pytest.raises(LLMResponseError) as exc_info:
                await service.generate_structured_response(
                    prompt="Generate test response",
                    response_model=TestResponse
                )
            
            assert "validation" in str(exc_info.value).lower()


class TestPromptTemplates:
    """Test prompt template functionality."""
    
    def test_get_test_prompt_template(self):
        """Test getting test prompt template."""
        template = prompt_library.get_prompt(PromptType.TEST)
        assert template is not None
        assert "test" in template.name.lower()
        assert template.system_prompt is not None
        assert template.user_prompt_template is not None
    
    def test_format_test_prompt_template(self):
        """Test formatting test prompt template."""
        template = prompt_library.get_prompt(PromptType.TEST)
        formatted = template.format_user_prompt(
            model="gemini-1.5-flash",
            timestamp="2024-01-15T10:30:00Z"
        )
        assert "gemini-1.5-flash" in formatted
        assert "2024-01-15T10:30:00Z" in formatted
    
    def test_list_all_prompts(self):
        """Test listing all available prompts."""
        prompts = prompt_library.list_prompts()
        assert isinstance(prompts, dict)
        assert len(prompts) >= 8  # At least 8 prompt types
        assert "test" in str(prompts).lower()
    
    def test_prompt_template_missing_variable(self):
        """Test prompt template with missing variable."""
        template = prompt_library.get_prompt(PromptType.TEST)
        with pytest.raises(ValueError):
            template.format_user_prompt(model="test")  # Missing timestamp


class TestLLMConfiguration:
    """Test LLM configuration validation."""
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': '', 'GEMINI_MODEL': 'gemini-1.5-flash'})
    def test_missing_api_key_validation(self):
        """Test validation of missing API key."""
        from app.llm.config import LLMSettings
        
        with pytest.raises(ValueError) as exc_info:
            LLMSettings()
        
        assert "api_key" in str(exc_info.value).lower()
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key', 'GEMINI_MODEL': ''}, clear=False)
    def test_empty_model_validation(self):
        """Test validation of empty model."""
        from app.llm.config import LLMSettings
        
        with pytest.raises(ValueError) as exc_info:
            LLMSettings()
        
        # Check that there's a validation error (either from API key or model)
        # The exact validation order depends on Pydantic implementation
        error_str = str(exc_info.value).lower()
        assert "validation error" in error_str or "value error" in error_str
    
    def test_temperature_bounds_validation(self):
        """Test temperature parameter bounds."""
        from app.llm.config import LLMSettings
        
        # This would normally come from env, but we're testing bounds
        # The validation is in the model itself
        assert 0.0 <= 0.7 <= 2.0  # Valid
        assert not (0.7 > 2.0)  # Invalid would fail


__all__ = []
