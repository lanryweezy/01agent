# 01Agent — Working Fork

This repository is a working fork of the open-source [01Agent](https://github.com/withneural/01agent) desktop AI agent by withneural, used here as a development and debugging workspace.

**This is not an original project.** Upstream source, documentation and credit belong to the original authors at [get01agent.com](https://www.get01agent.com).

## What 01Agent is

A desktop AI assistant that performs real computer-use tasks — typing, clicking, browser navigation, form filling and email — driven by large language models. It runs a FastAPI + PostgreSQL backend with an Electron and React frontend, uses `pyautogui` for foreground desktop automation and Playwright for browser control, and supports Anthropic, OpenAI, Azure OpenAI, AWS Bedrock, Gemini and Ollama. It is multimodal (text and vision) and built around modular agents: Planner, Classifier, Suggestor and Title.

## Work in this fork

Debugging and correctness work on the React frontend, primarily around hook dependency correctness in the Electron app's shared component layer — see [`plan.md`](./plan.md) for the analysis behind a targeted fix to `src/components/Elements/Selects/index.js`, memoising `getItemFromValue` and `getMultipleSelectionText` with `useCallback` and removing the `react-hooks/exhaustive-deps` suppressions rather than working around them.

Comparison notes against UI-TARS are in [`docs/UI_TARS_COMPARISON.md`](./docs/UI_TARS_COMPARISON.md).

## Repository layout

```
01agent/
├── backend/        FastAPI + PostgreSQL backend
├── desktop/
│   ├── 01agent-app/  React frontend inside Electron
│   └── aiagent/      Python automation (pyautogui)
├── landing-page/
└── streamlit_app/
```

Full setup instructions, prerequisites and OS notes are in [`01agent/README.md`](./01agent/README.md).

## License

Upstream license applies — see [`01agent/LICENSE`](./01agent/LICENSE).
