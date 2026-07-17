# Clipify Web Demo

This demo is a sandbox for trying Clipify from a browser. It is not a production service and it is intentionally limited to keep running costs near zero on free hosting.

## Hard limits enforced
- Maximum video length: 3 minutes
- Maximum file size: 100MB
- Maximum clip count: 3
- Rate limit: 3 successful generations per session/IP per hour
- Processing is forced to local Whisper only; no cloud AI providers or API keys are exposed in the UI

These limits exist because this demo runs on free hosting with no budget for paid APIs or long-running jobs.

## Deploying to Hugging Face Spaces
1. Create a new Space with SDK = Gradio.
2. Upload or push the contents of the webdemo folder as the app source.
3. Set the Space hardware to CPU basic (free tier).

Anyone who wants heavier usage, longer videos, or cloud AI providers should run Clipify locally via the CLI instead, since the maintainer does not subsidize public API costs.
