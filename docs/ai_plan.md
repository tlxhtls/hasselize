# RTX 5090 기반 고속 이미지 증강 계획 (Hasselblad 화질 구현)

### 1. 핵심 추천 모델
*   **모델**: Flux.1-Schnell (FP4 양자화 버전)
*   **가속 하드웨어**: RTX 5090 Blackwell 5세대 텐서 코어 (FP4 연산 최적화)
*   **스타일**: Hasselblad 전용 LoRA (`c41_hasselblad_portra400` 또는 `Hasselblad camera style F1D`)

### 2. 가속 워크플로우 (Python Backend)
*   **프레임워크**: Python Diffusers 직접 호출 (ComfyUI 오버헤드 제거) [1]
*   **최적화 엔진**: NVIDIA TensorRT-RTX (JIT 컴파일 방식)
*   **처리 속도**: 256x256px 해상도 기준 1초 이내 (FP4 가속 시 FP8 대비 최대 3.1배 향상)

### 3. 세부 설정 및 전략
*   **피사체 유지**: img2img 파이프라인에서 Denoising Strength를 0.3~0.4로 고정
*   **심도 및 질감**: 프롬프트에 `medium format`, `80mm f/2.8`, `creamy bokeh` 토큰 포함
*   **해상도**: 256x256px 소형 사이즈로 추론 지연 시간 최소화

### 4. 고급 API 대안
*   **솔루션**: NanoBanana Pro (Gemini 3 Pro Image) [2, 3]
*   **용도**: 4K 업스케일링이 필요하거나 인물 일관성을 극한으로 유지해야 할 때 활용
