# AI Prompt Sender

AI Prompt Sender - Send prompts to multiple AI providers with comprehensive logging
Supports: OpenAI, Anthropic (Claude), Google Gemini, and Perplexity

## Features

- **Multi-Provider Support**: Send prompts to OpenAI, Anthropic, Google Gemini, and Perplexity
- **Database Integration**: Store conversations in MongoDB or Xano
- **Comprehensive Logging**: Configurable logging with multiple levels and file output
- **Response Validation**: Built-in validation for structured responses
- **Database Management**: Command-line tools for managing stored conversations

## Setup

### Environment Variables

Create a `.env` file in the same directory as the script with your API keys:

```bash
# AI Service API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Database Configuration
DATABASE_PROVIDER=mongodb  # or "xano"
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=ai_prompt_sender
XANO_BASE_URL=https://your-workspace.xano.com/api:v1
XANO_API_TOKEN=your_xano_api_token_here  # Optional

# Logging Configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/ai_prompt_sender.log  # Optional - enables file logging
```

### Logging Configuration

The application includes a comprehensive logging system that can be configured via environment variables:

#### Log Levels
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about program execution
- `WARNING`: Warning messages for potentially problematic situations
- `ERROR`: Error messages for serious problems
- `CRITICAL`: Critical errors that may prevent the program from running

#### Log Output
- **Console**: All log messages are displayed in the console by default
- **File**: Enable file logging by setting `LOG_FILE` environment variable
- **Format**: `timestamp - logger_name - level - message`

#### Examples

```bash
# Basic usage with INFO level (default)
python ai_prompt_sender.py

# Debug mode with detailed logging
LOG_LEVEL=DEBUG python ai_prompt_sender.py

# Enable file logging
LOG_FILE=logs/app.log LOG_LEVEL=INFO python ai_prompt_sender.py

# Warning level only (suppresses INFO and DEBUG)
LOG_LEVEL=WARNING python ai_prompt_sender.py
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python ai_prompt_sender.py
```

### Database Management

```bash
# Interactive mode
python database_manager.py

# Command-line mode
python database_manager.py stats
python database_manager.py list 10
python database_manager.py show <conversation_id>
python database_manager.py search "query"
python database_manager.py export <conversation_id>
python database_manager.py delete <conversation_id>
```

## Example Usage

```python
from ai_prompt_sender import AIPromptSender, Provider, PromptMessage
from services import print_response

async def main():
    """Example usage of the AI Prompt Sender"""
    
    sender = AIPromptSender()
    
    print("Example 1: Simple user prompt")
    messages = [
        PromptMessage(role="user", content="What is the capital of France?")
    ]
    
    responses = await sender.send_to_all(messages)
    for response in responses:
        print_response(response)
    
    print("\n\nExample 2: System + User prompt")
    messages = [
        PromptMessage(role="system", content="You are a helpful assistant that responds in a pirate accent."),
        PromptMessage(role="user", content="Tell me about artificial intelligence.")
    ]
    
    responses = await sender.send_to_all(messages)
    for response in responses:
        print_response(response)
    
    print("\n\nExample 3: Send to specific provider (OpenAI)")
    response = await sender.send_to_provider(
        Provider.OPENAI,
        [PromptMessage(role="user", content="Explain quantum computing in simple terms.")]
    )
    print_response(response)
``` 