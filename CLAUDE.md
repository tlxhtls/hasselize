# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Hasselize** is an AI-powered professional photography suite that transforms ordinary smartphone photos into Medium Format camera-grade images with superior sharpness and depth of field.

Vision: "Everyone can experience Medium Format camera quality in their pocket."

## Repository Structure

Planned monorepo structure (not yet implemented):

```
/hasselize
├── /apps
│   ├── /web          # Next.js Frontend (App Router, Tailwind CSS, Supabase)
│   └── /ai-backend   # FastAPI Python Backend
├── /docs             # PRD, design guides, API specs
├── .gitignore        # Security-focused
├── README.md         # Project landing page
└── docker-compose.yml
```

## Tech Stack

**Frontend:**
- Next.js (App Router)
- Tailwind CSS
- Supabase (Database/Auth)

**Backend AI:**
- FastAPI (Python 3.10+)
- AI Models:
  - Flux.1 [Flash/Schnell] - Primary model for Medium Format quality
  - Z-image Turbo - SDXL-based ultra-fast generation
  - ControlNet - For preserving original composition and human forms
- RTX 5090 GPU for high-speed inference

**Infrastructure:**
- Cloudflare R2 (Storage)

## AI Processing Pipeline

1. User uploads photo (Low-Res first for feedback)
2. ControlNet preserves original structure (Canny, Depth, IP-Adapter)
3. Flux.1 applies Medium Format aesthetic
4. Optional High-Res upscaling for paid users

## Security & Prompt Management

**Critical:** Prompts are core competitive advantage. Use 3-tier protection strategy:

1. **Tier 1 (Simple):** `.env` files for basic system prompts
   - Use `os.getenv("SYSTEM_PROMPT")` in code

2. **Tier 2 (Recommended):** Supabase database storage
   - Table structure: `prompts(id, version, camera_model, content)`
   - Enables A/B testing without code changes
   - Never exposed to GitHub

3. **Tier 3 (Complex):** Local JSON files excluded by `.gitignore`
   - For complex JSON-structured prompts
   - Path: `apps/ai-backend/config/secret_prompts.json`

**Required `.gitignore` entries:**
```
# Secrets & Config
.env
.env.local
.env.*.local
config/secret_*.json

# AI Weights
*.ckpt
*.safetensors
*.pt
/apps/ai-backend/weights/
```

## Core Features (MVP)

1. **AI Photo Transformation:** "Hasselblad Look" with ControlNet structure preservation
2. **Before/After Feed:** Slider-based comparison cards
3. **Social Sharing:** Direct sharing to Instagram, Threads, etc.

## Future Features

- Multiple camera model styles (Leica M, Zeiss, Fujifilm GFX)
- High-resolution upscaling (2K/4K) for premium users
- Batch processing using idle GPU resources
- E-commerce integration ("Buy the Look" - affiliate camera gear sales)

## Monetization

- **Standard:** Low-res unlimited transformations, basic Hasselize style
- **Premium:** High-res (4K) downloads, exclusive LoRA styles, priority queue
- **Commerce:** Affiliate marketing through camera gear partnerships

## Development Priorities

When implementing, focus on:

1. **Speed:** <5 seconds total user wait time, <1.5s inference latency
2. **Quality:** Visibly improved sharpness and depth perception
3. **Virality:** SNS sharing frequency of "Hasselized" photos

## Important Notes

- **Current Status:** Documentation only - no code implementation yet
- **Performance Target:** RTX 5090 GPU with TensorRT optimization
- **Prompt Strategy:** Keep camera-specific prompts out of version control
- **Data:** Store prompts in Supabase for runtime A/B testing capability
