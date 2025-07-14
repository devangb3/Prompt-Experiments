# AI Prompt Sender

AI Prompt Sender - Send prompts to multiple AI providers
Supports: OpenAI, Anthropic (Claude), Google Gemini, and Perplexity

## Setup

Make sure to set the following environment variables:
- OPENAI_API_KEY (for OpenAI)
- ANTHROPIC_API_KEY (for Anthropic/Claude)
- GEMINI_API_KEY (for Google Gemini)
- PERPLEXITY_API_KEY (for Perplexity)

Create a `.env` file in the same directory as the script with:
```
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
PERPLEXITY_API_KEY=your-perplexity-api-key-here
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python ai_prompt_sender.py
```

## Example Usage

```bash
python example_usage.py
```

## Example Usage

```python
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