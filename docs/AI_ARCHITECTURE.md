# PocketSmart AI — AI Architecture & Prompt Engineering

## Overview

PocketSmart AI integrates Google Gemini models (Gemini 2.5 Flash / Gemini 1.5 Pro) with structured JSON generation and deterministic budget constraints.

---

## Architecture Pipeline

```
               ┌───────────────────────────────┐
               │    User Request & Parameters   │
               └──────────────┬────────────────┘
                              │
                              ▼
               ┌───────────────────────────────┐
               │     BudgetService Allocation   │
               │   (Deterministic Category %)  │
               └──────────────┬────────────────┘
                              │
                              ▼
               ┌───────────────────────────────┐
               │     Prompt Engineering Layer  │
               │   - System instructions       │
               │   - Structured Output Schema  │
               │   - Vision/Image parts if any │
               └──────────────┬────────────────┘
                              │
                              ▼
               ┌───────────────────────────────┐
               │        Gemini 2.5 Flash       │
               └──────────────┬────────────────┘
                              │ JSON Stream / Text
                              ▼
               ┌───────────────────────────────┐
               │  JSON Parser & Repair Layer   │
               │  - Markdown strip             │
               │  - Schema validation          │
               │  - Safe fallback defaults     │
               └──────────────┬────────────────┘
                              │
                              ▼
               ┌───────────────────────────────┐
               │  Recommendation & Catalog     │
               │  Matching Engine              │
               └──────────────┬────────────────┘
                              │
                              ▼
               ┌───────────────────────────────┐
               │  Calculated Final Response    │
               └───────────────────────────────┘
```

---

## Key Prompt Design Principles

1. **Strict JSON Schema Enforcement**:
   All prompts specify exact JSON output structures and forbid conversational filler or unformatted prose.

2. **Multimodal Visual Styling (Jewelry Planner)**:
   When an outfit image is provided by the user, the image binary/URL is passed to the Gemini Vision model alongside instructions to analyze:
   - Base outfit fabric color and undertones.
   - Neckline geometry (sweetheart, V-neck, boat neck, collar) to recommend matching necklace lengths.
   - Embroidery metals (antique gold, silver, rose gold, pearls).

3. **Defensive AI Repair**:
   `GeminiService` incorporates an automated repair layer (`JsonParser`) that:
   - Strips ````json ``` blocks.
   - Parses partially damaged JSON strings.
   - Inserts sensible defaults for missing fields.
   - Falls back gracefully to heuristic recommendations in case of model rate-limiting or service interruptions.
