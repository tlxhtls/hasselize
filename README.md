# Hasselize

**AI-powered professional photography suite** that transforms ordinary smartphone photos into Medium Format camera-grade images with superior sharpness and depth of field.

> **Vision**: "Everyone can experience Medium Format camera quality in their pocket."

## 🚀 Quick Start

### Prerequisites

- **Node.js 20+** (for frontend)
- **Python 3.11+** (for backend)
- **RTX 5090 GPU** (or CUDA-compatible GPU)
- **Supabase account** (for database/auth)
- **Cloudflare R2 account** (for storage)

### 1. Clone & Install

```bash
# Clone repository
git clone https://github.com/yourusername/hasselize.git
cd hasselize

# Install frontend dependencies
cd apps/web
npm install

# Install backend dependencies
cd ../ai-backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment templates
cp apps/web/.env.local.example apps/web/.env.local
cp apps/ai-backend/.env.example apps/ai-backend/.env

# Edit with your credentials
# - Supabase URL and keys
# - Cloudflare R2 credentials
# - HuggingFace token (for FLUX.1-Schnell)
```

### 3. Setup Database

```bash
# Run Supabase migration
psql -h your-project.supabase.co -U postgres -d postgres -f supabase/migrations/001_initial_schema.sql
```

### 4. Run Development Servers

```bash
# Terminal 1: AI Backend
cd apps/ai-backend
uvicorn api.main:app --reload

# Terminal 2: Next.js Frontend
cd apps/web
npm run dev
```

Visit:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
hasselize/
├── apps/
│   ├── web/              # Next.js 15 frontend (PWA)
│   └── ai-backend/       # FastAPI backend (FLUX.1-Schnell)
├── supabase/
│   └── migrations/       # Database migrations
├── docs/                 # Documentation
├── docker-compose.yml    # Multi-service deployment
└── README.md
```

## 🎯 Tech Stack

### Frontend
- **Next.js 15** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Supabase Auth**
- **PWA** (Progressive Web App)

### Backend
- **FastAPI** (Python 3.11)
- **FLUX.1-Schnell** (AI Model)
- **Diffusers** (HuggingFace)
- **PyTorch** (CUDA 12.4)
- **Cloudflare R2** (Storage)

### Infrastructure
- **Supabase** (PostgreSQL, Auth)
- **Cloudflare R2** (S3-compatible storage)
- **Docker Compose** (Local development)

## 🎨 Camera Styles

- **Hasselblad X2D** (Free) - Medium format depth
- **Leica M Series** (Premium) - High contrast street
- **Zeiss Lenses** (Premium) - Exceptional sharpness
- **Fujifilm GFX** (Premium) - Film simulations

## 🔐 Security

- **Row Level Security** (RLS) on Supabase
- **3-tier prompt management** (env → database → local JSON)
- **Never commit** model weights or API keys
- See `.gitignore` for protected files

## 🐳 Docker Deployment

```bash
# Build and start all services
docker-compose up --build

# Backend only (requires GPU)
docker-compose up ai-backend

# Frontend only
docker-compose up web
```

## 📊 AI Spec (from docs/ai_plan.md)

- **Model**: FLUX.1-Schnell (FP4 quantized)
- **Pipeline**: img2img with Denoising Strength 0.35
- **Resolution**: 256×256 (preview), 512×512 (standard), 1024×1024 (high)
- **Target**: <1s inference, <5s total request time
- **GPU**: RTX 5090 with TensorRT optimization

## 🧪 Testing

```bash
# Backend tests
cd apps/ai-backend
pytest

# Frontend tests (TODO)
cd apps/web
npm test
```

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Credits

- **FLUX.1-Schnell** by Black Forest Labs
- **Diffusers** by HuggingFace
- **Supabase** for backend infrastructure

---

Built with ❤️ by the Hasselize team
