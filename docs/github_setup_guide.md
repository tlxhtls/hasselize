# Hasselize: GitHub Repository Setup Guide
(Hasselize: GitHub Repository Setup Guide해커톤 프로젝트의 성공적인 론칭과 팀 협업을 위한 깃허브 설정 가이드입니다.1. Public vs Private 결정권장: Public (공개)이유: 해커톤은 결과물뿐만 아니라 '과정'을 보여주는 것이 중요합니다. 공개 레포지토리는 심사위원에게 기술력을 어필하기 좋고, 추후 포트폴리오로 활용하기 유리합니다.주의사항: 5090 서버 접속 정보, Supabase API Key, Cloudflare Secret 등은 절대 코드에 포함하지 말고 .env 파일로 관리해야 합니다.2. 영업기밀(프롬프트) 보안 관리 전략프롬프트는 Hasselize의 핵심 경쟁력입니다. 이를 보호하기 위한 3단계 전략을 제안합니다.2.1 단계: .env 활용 (가장 간단함)간단한 시스템 프롬프트는 환경 변수로 관리합니다.AI 백엔드의 .env에 SYSTEM_PROMPT="Your Secret Prompt Here" 추가.코드에서는 os.getenv("SYSTEM_PROMPT")로 호출.2.2 단계: Supabase DB 활용 (권장)프롬프트를 DB 테이블에 저장하고 런타임에 불러옵니다.장점: 코드 수정 없이 프롬프트를 즉시 업데이트(A/B 테스트 가능)할 수 있으며, 깃허브에는 절대 노출되지 않습니다.prompts 테이블 구조: id, version, camera_model (Leica, Hasselblad 등), content.2.3 단계: .gitignore를 통한 로컬 설정 파일 분리복잡한 JSON 구조의 프롬프트가 필요하다면 별도의 파일을 만들고 Git 추적에서 제외합니다.apps/ai-backend/config/secret_prompts.json 생성..gitignore에 해당 경로 추가.3. 권장 디렉토리 구조 (Monorepo)/hasselize
├── /apps
│   ├── /web          # Next.js (Frontend + Supabase Client)
│   └── /ai-backend   # FastAPI (Python + Flux.1/Z-image)
├── /docs             # PRD, 디자인 가이드, API 명세
├── .gitignore        # 보안의 핵심!
├── README.md         # 프로젝트 대문
└── docker-compose.yml
4. 필수 파일 세팅 (.gitignore)프로젝트 루트에 아래 내용을 반드시 포함하세요.# Dependency
node_modules/
venv/
.python-version

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
5. README.md (프로젝트의 얼굴)# 📸 Hasselize
> **Ordinary to Medium Format: AI-powered Professional Photography Suite**

## ✨ Core Vision
평범한 스마트폰 사진을 중형 카메라(Medium Format)급의 선예도와 심도를 가진 예술 작품으로 재구성합니다.

## 🛠 Tech Stack
- **Frontend:** Next.js, Tailwind CSS, Supabase
- **Backend:** FastAPI, Python 3.10+
- **AI Models:** Flux.1 [Flash], ControlNet, SDXL-Turbo
- **Infrastructure:** RTX 5090 GPU, Cloudflare R2
6. 초기화 명령어 (CLI)git init
mkdir -p apps/web apps/ai-backend docs
touch README.md .gitignore
git add .
git commit -m "chore: initial project structure with security focus"
git branch -M main
git remote add origin [https://github.com/your-username/hasselize.git](https://github.com/your-username/hasselize.git)
git push -u origin main

