# Prompt Experiments

Prompt Experiments is a provider-agnostic harness for comparing LLM responses
and running structured cross-provider evaluation across OpenAI, Anthropic, and
Gemini.

It captures prompts, responses, provider and model identity, latency, token
usage, errors, structured judge output, and experiment metadata. Cross-provider
judging avoids asking a model to grade its own response, while Pydantic schemas
keep evaluation results machine-readable.

```text
prompt → provider adapters → responses
                         ↓
               cross-provider judge
                         ↓
        structured scores + provenance
                         ↓
                 MongoDB or Xano
```

## Evaluation model

The active judge routing is explicit:

| Response provider | Judge provider |
| --- | --- |
| OpenAI | Anthropic |
| Anthropic | Gemini |
| Gemini | OpenAI |

Each judgment returns a score from 1 to 5 plus a written reason for:

- clarity
- specificity
- relevance
- actionability
- approachability

The current judge prompt is specialized for evaluating generated BrainWorkout
feedback. The provider and persistence layers are reusable, but a different
evaluation domain should supply its own judge prompt and result schema.

## Quickstart

Create and activate a virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` with the provider keys you want to enable:

```dotenv
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...

DATABASE_PROVIDER=mongodb
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=ai_prompt_sender

LOG_LEVEL=INFO
# LOG_FILE=logs/prompt_experiments.log
```

Provider services are registered only when their API key is present. A minimal
comparison can run without persistence:

```python
import asyncio

from ai_prompt_sender import AIPromptSender
from services import PromptMessage


async def main() -> None:
    sender = AIPromptSender(enable_database=False)
    responses = await sender.send_to_all(
        [PromptMessage(role="user", content="Explain optimistic concurrency control.")]
    )
    for response in responses:
        print(response.provider, response.model, response.error or response.content)
    await sender.close()


asyncio.run(main())
```

## Structured judging

Use `JudgeService` when the response should be evaluated by a different
provider:

```python
import asyncio

from services import Provider
from services.judge_service import JudgeService


async def evaluate() -> None:
    judge = JudgeService(enable_database=False)
    judgment = await judge.judge_response(
        Provider.GEMINI,
        original_response="The response text to evaluate",
        ui_request="The original user prompt",
    )
    print(judgment.content)


asyncio.run(evaluate())
```

Provider services request a structured `JudgeResponse` through each provider's
tool/function-calling interface. The Pydantic schema rejects malformed judge
payloads instead of treating arbitrary text as a successful evaluation.

## Persisted records

Set `DATABASE_PROVIDER` to `mongodb` or `xano`. Both backends use the same
conversation-shaped contract:

```text
conversation
├── conversation_id
├── system_prompt
├── messages[]
├── responses[]
│   ├── provider
│   ├── model
│   ├── response
│   ├── tokens_used
│   ├── error
│   └── response_time_ms
├── ratings
│   └── provider_ratings
│       ├── score
│       ├── categories
│       └── overall_reason
└── metadata
```

MongoDB-to-Xano migration and verification utilities live under `database/`;
see `README_XANO_MIGRATION.md` for the migration workflow.

## Database management

The database CLI can inspect and manage persisted experiments:

```bash
python database_manager.py stats
python database_manager.py list 10
python database_manager.py show <conversation_id>
python database_manager.py search "query"
python database_manager.py export <conversation_id>
python database_manager.py delete <conversation_id>
```

## Adding a provider

1. Add the provider to `services.types.Provider`.
2. Implement a `BaseAIService` adapter under `services/`.
3. Register it in `services.service_factory.AIServiceFactory`.
4. Define its default model and structured-output behavior.
5. Decide which different provider will judge its responses.
6. Verify that errors are returned in `AIResponse.error` and persisted without
   being mistaken for model output.

## Adding an evaluation dimension

1. Add the field to `models/JudgeResponse.py`.
2. Define the dimension and score meaning in the judge system prompt.
3. Add it to the rating normalization in `AIPromptSender.save_to_database`.
4. Update downstream consumers of `ratings.provider_ratings`.

Keeping the schema, prompt, and persistence mapping aligned prevents a new
dimension from appearing in model output but disappearing from stored results.

## Logging

Logs go to the console by default. Set `LOG_FILE` for file output and
`LOG_LEVEL` to `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`.

```bash
LOG_FILE=logs/prompt_experiments.log LOG_LEVEL=DEBUG python ai_prompt_sender.py
```

## Error behavior

- A missing provider key leaves that provider unregistered.
- Calling an unavailable provider returns an `AIResponse` with `error` set.
- If no providers are available, `send_to_all` returns an explicit error
  response.
- Provider parsing and validation failures are represented as failed
  `AIResponse` values and can be persisted beside successful responses.
- Database write failures are logged; direct Xano service operations can also
  raise their underlying request error.

## Current boundaries

- The active factory exposes OpenAI, Anthropic, and Gemini.
- A `PerplexityService` adapter exists, but Perplexity is not currently present
  in the `Provider` enum or registered by the factory.
- Cross-provider judge routing currently covers OpenAI, Anthropic, and Gemini.
- The bundled `ai_prompt_sender.py` demo expects application-specific
  BrainWorkout input and is not the generic quickstart.
