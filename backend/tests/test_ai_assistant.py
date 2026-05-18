import os
from unittest.mock import patch
from app.services.ai_assistant import get_api_key_for_model, get_effective_model_and_key
from app.core.config import settings

def test_get_api_key_for_model():
    # 1. Test OpenRouter resolution
    with patch.object(settings, 'OPENROUTER_API_KEY', 'test_openrouter_key'):
        assert get_api_key_for_model('openrouter/anthropic/claude-3.5-sonnet') == 'test_openrouter_key'

    # 2. Test Anthropic/Claude resolution
    with patch.object(settings, 'ANTHROPIC_API_KEY', 'test_anthropic_key'):
        assert get_api_key_for_model('anthropic/claude-3-5-sonnet') == 'test_anthropic_key'
        assert get_api_key_for_model('claude-3-5-sonnet-20241022') == 'test_anthropic_key'

    # 3. Test Gemini resolution
    with patch.object(settings, 'GEMINI_API_KEY', 'test_gemini_key'):
        assert get_api_key_for_model('gemini/gemini-2.5-flash') == 'test_gemini_key'

    # 4. Test OpenAI resolution
    with patch.object(settings, 'OPENAI_API_KEY', 'test_openai_key'):
        assert get_api_key_for_model('openai/gpt-4o-mini') == 'test_openai_key'
        assert get_api_key_for_model('gpt-4o') == 'test_openai_key'

def test_get_effective_model_and_key_fallback():
    # Test that model is automatically routed through OpenRouter if only OpenRouter API key is set
    with patch.object(settings, 'OPENROUTER_API_KEY', 'test_openrouter_key'):
        with patch.object(settings, 'OPENAI_API_KEY', None):
            eff_model, api_key = get_effective_model_and_key('openai/gpt-4.1-mini')
            assert eff_model == 'openrouter/openai/gpt-4.1-mini'
            assert api_key == 'test_openrouter_key'

    # Test that model is NOT routed through OpenRouter if direct provider key IS set
    with patch.object(settings, 'OPENROUTER_API_KEY', 'test_openrouter_key'):
        with patch.object(settings, 'OPENAI_API_KEY', 'test_openai_key'):
            eff_model, api_key = get_effective_model_and_key('openai/gpt-4.1-mini')
            assert eff_model == 'openai/gpt-4.1-mini'
            assert api_key == 'test_openai_key'
