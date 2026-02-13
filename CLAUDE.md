# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Hasselize** is an AI-powered professional photography suite that transforms ordinary smartphone photos into Medium Format camera-grade images with superior sharpness and depth of field.

Vision: "Everyone can experience Medium Format camera quality in their pocket."

## Repository Structure

Active monorepo structure:

```
/hasselize
├── /apps
│   ├── /web          # Next.js 15 Frontend (PWA, App Router, Tailwind CSS)
│   └── /ai-backend   # FastAPI Python Backend (FLUX.1-Schnell)
├── /supabase         # Database migrations
├── /docs             # PRD, design guides, API specs
├── .github/workflows # CI/CD pipelines
└── docker-compose.yml
```

## Development Commands

### Frontend (apps/web/)
```bash
npm run dev      # Start development server (localhost:3000)
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # ESLint check
```

### Backend (apps/ai-backend/)
```bash
uvicorn api.main:app --reload    # Start development server (localhost:8000)
ruff check .                      # Linting
black --check .                   # Format check
pytest                            # Run tests
```

### Docker (Project root)
```bash
docker-compose up --build         # Start all services
docker-compose up ai-backend     # Backend only (requires GPU)
docker-compose up web             # Frontend only
```

## Tech Stack

**Frontend:**
- Next.js 15 (App Router, React 19, TypeScript)
- Tailwind CSS
- Supabase (Auth + Database)
- PWA with next-pwa

**Backend AI:**
- FastAPI (Python 3.11+)
- PyTorch 2.5.0 with CUDA 12.4
- FLUX.1-Schnell (primary model, BF16)
- LoRA style injection for camera looks
- RTX 5090 GPU optimized (xformers, TensorRT)

**Infrastructure:**
- Cloudflare R2 (Storage)
- Docker Compose (Multi-service deployment)

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

## Architecture Overview

### Backend Service Layer

The AI backend follows a layered service architecture:

- **`core/`**: Configuration, GPU management, logging, security
  - `config.py`: Pydantic-based settings with environment variable support
  - `gpu_manager.py`: Singleton GPU memory management for RTX 5090
  - `security.py`: Rate limiting (10 req/60s default), CORS

- **`services/`**: Business logic layer
  - `model_loader.py`: Lazy-loading FLUX.1-Schnell with LoRA injection
  - `image_service.py`: Complete transformation pipeline orchestration
  - `storage_service.py`: Cloudflare R2 S3-compatible storage

- **`api/routes/`**: FastAPI endpoints
  - `/api/v1/transform`: Main image transformation endpoint
  - `/api/v1/transform/url`: Transform from URL
  - `/api/v1/health`: Health check with GPU stats

- **`models/`**: Request/response schemas and enums
  - `enums.py`: CameraStyle, ResolutionMode, ModelType, TransformationStatus

### Frontend Architecture

- **App Router** with server/client components
- **`app/transform/page.tsx`**: Main transformation UI with Before/After slider
- **`components/`**: Reusable UI components (ImageUploader, BeforeAfterSlider)
- **`lib/api/`**: Backend API client with type definitions

### Configuration System

**Backend** (`core/config.py`):
- Environment-based via Pydantic Settings
- Key env vars: `MODEL_NAME`, `CUDA_VISIBLE_DEVICES`, `GPU_MEMORY_FRACTION`
- Three-tier prompt management (see Security section below)

**Frontend** (`next.config.js`):
- PWA enabled with next-pwa
- Remote image patterns for R2 and Supabase domains
- Turbopack for development

### AI Pipeline Flow

```
1. Upload → 2. Validate → 3. Resize → 4. Build Prompts → 5. Apply LoRA → 6. Inference → 7. Upload to R2 → 8. Return URLs
```

- **Resolution modes**: preview (256×256), standard (512×512), high (1024×1024)
- **Denoising strength**: 0.35 (configurable 0.3-0.4 range)
- **Inference steps**: 4 for FLUX.1-Schnell (ultra-fast)
- **Target latency**: <1s inference, <5s total

### Camera Styles (LoRA)

Styles are injected via LoRA weights from `lora_cache_dir`:
- `hasselblad`: C41 Portra 400 style (free)
- `leica_m`: High contrast street (premium)
- `zeiss`: Exceptional sharpness (premium)
- `fujifilm_gfx`: Film simulations (premium)

## Code Conventions

### Backend (Python)
- **Formatting**: Black (line-length: 100)
- **Linting**: Ruff (E, F, I, N, W rules)
- **Type hints**: Required for all public functions
- **Logging**: Structured JSON logging in production via `core/logging.py`

### Frontend (TypeScript)
- **Strict mode** enabled
- **Path alias**: `@/*` maps to project root
- **Client components**: `'use client'` directive for interactive components

## Important Notes

- **GPU Requirement**: RTX 5090 or CUDA-compatible GPU required for backend
- **Model Cache**: Models cached in `/app/cache/models` within Docker
- **Performance Target**: <1s inference, <5s total request time
- **Prompt Strategy**: Keep camera-specific prompts out of version control
- **CI/CD**: GitHub Actions run on push/PR to main/master branches
