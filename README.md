# CodeAtlas 🗺️

> **Understand any codebase. Visually. Intelligently.**

CodeAtlas is an AI-powered codebase intelligence platform that turns a GitHub repository into an interactive map of its architecture, dependencies, code, and execution flows.

Paste a repository → analyze it → explore the system → ask AI questions.

## ✨ What it does

* 🕸️ **Interactive Architecture Graph** — Visualize components, services, dependencies, and relationships.
* 🔍 **Semantic Code Search** — Find relevant code and understand why it matters.
* 🧠 **AI Codebase Chat** — Ask questions about how the repository works.
* 📊 **Call & Dependency Graphs** — Explore relationships from architecture down to functions.
* ⚠️ **Impact Analysis** — Understand what could break before changing a component.
* 📖 **AI Onboarding** — Get an architectural explanation of an unfamiliar codebase.
* 💻 **Code Explorer** — Jump from graph nodes and AI answers directly to relevant source code.

## 🚀 Core Experience

```text
GitHub Repository
       ↓
Repository Analysis
       ↓
Codebase Intelligence
       ↓
┌─────────────┬─────────────┬─────────────┐
│ Architecture│    Search   │     Chat    │
│    Graph    │    Code     │     AI      │
└─────────────┴─────────────┴─────────────┘
       ↓
Understand • Explore • Debug • Modify
```

## 🎯 The Goal

CodeAtlas combines **graph-based code intelligence, semantic search, and AI** into one interface so developers can answer:

* Where is this implemented?
* How does this feature work?
* What depends on this component?
* What happens when this API is called?
* What could break if I change this?

The graph isn't just a visualization — it is part of the underlying codebase intelligence model.

## 🛠️ Status

🚧 **Early development**

More features and implementation details coming soon.
## Day 4 — Relationship Resolver & Code Graph

CodeAtlas now builds a graph representing relationships between entities in a repository.

### Graph Node Types

- FILE
- CLASS
- FUNCTION
- METHOD
- EXTERNAL

### Relationship Types

- CONTAINS
- INHERITS
- CALLS
- IMPORTS

### Graph API

Get the complete graph:

`GET /repositories/{repository_id}/graph?filter=ALL`

Supported filters:

- ALL
- CLASS
- FUNCTION
- CALLS
- IMPORTS

### Graph Features

- Deterministic node IDs
- File → class/function relationships
- Class inheritance relationships
- Function and method call relationships
- Import relationships
- External nodes for unresolved calls/imports
- Graph statistics
- Graph filtering

### Testing

Day 4 graph and parser tests:

`14 passed`