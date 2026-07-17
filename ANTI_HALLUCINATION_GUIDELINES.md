# Anti-Hallucination Guidelines

Clipify can reduce AI guesswork by preferring deterministic, transcript-focused processing and by using local/offline providers when available.

## When to enable anti-hallucination mode

- Use `--anti-hallucination` on the command line.
- Or set `ANTI_HALLUCINATION=true` in your `.env` or environment.
- This tells Clipify to prefer local-safe processing and avoid remote model scoring when a trusted local provider is available.

## Best practices for safer results

- Pin a provider you trust with `--ai PROVIDER` or `AI_PROVIDER`.
- Prefer the local provider (`--ai local`) for the safest results when available.
- Keep text prompts narrowly scoped to the transcript and clip content.
- Avoid open-ended, speculative prompts that invite invented facts.
- Validate timestamps, clip titles, or sensitive outputs manually.

## Provider guidance

- `local`: Best for offline or locked-down environments.
- `openai`, `anthropic`, `groq`, `mistral`, and others: use lower temperature or default deterministic settings if supported.
- If you need a cloud provider, choose one you know is reliable for transcript-based analysis.

## Practical checklist

- [ ] Confirm `--ai` or `AI_PROVIDER` is set to a provider you trust.
- [ ] Enable `--anti-hallucination` or `ANTI_HALLUCINATION=true` when using remote AI.
- [ ] Prefer local processing for final output generation when accuracy matters.
- [ ] Keep generated clip descriptions tied to the transcript text.
- [ ] Review the final output before publishing or sharing.

## Why this matters

Anti-hallucination mode helps Clipify avoid making up context or details that are not present in the source video transcript. It is especially useful when producing content for news, product demos, or audience-facing clips that must remain factual.
