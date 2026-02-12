# LoRA Setup Guide for Hasselize

## Overview

Hasselize uses LoRA (Low-Rank Adaptation) weights to apply different camera styles to images. Each camera style (Hasselblad, Leica M, Zeiss, Fujifilm GFX) has its own LoRA file.

## Directory Structure

```
apps/ai-backend/cache/
├── models/          # Base FLUX.1-Schnell model (auto-downloaded)
└── lora/            # Camera style LoRA files (manual setup required)
    ├── c41_hasselblad_portra400.safetensors
    ├── leica_m_style.safetensors
    ├── zeiss_otus_style.safetensors
    └── fujifilm_gfx_style.safetensors
```

## LoRA File Requirements

1. **Format**: `.safetensors` format (recommended for security)
2. **Compatibility**: FLUX.1-Schnell compatible
3. **Training**: Trained on photography style transfer
4. **Size**: Typically 50-200MB per file

## Finding LoRA Files

### Option 1: Civitai (Recommended)

1. Visit https://civitai.com/tag/loras
2. Search for camera styles:
   - "Hasselblad" or "Medium Format"
   - "Leica" or "M Series"
   - "Zeiss" or "Otus"
   - "Fujifilm" or "GFX"
3. Filter for FLUX.1 compatible models
4. Download `.safetensors` files
5. Rename to match expected filenames (see below)

### Option 2: HuggingFace

Search for FLUX-compatible LoRAs:
- https://huggingface.co/models?search=lora+flux
- https://huggingface.co/models?search=photography+lora

### Option 3: Train Custom LoRAs

Train your own camera style LoRAs using:
- **Dataset**: 50-100 sample photos from target camera
- **Training**: Kohya LoRA trainer or FLUX training scripts
- **Output**: Export as `.safetensors`

## Expected Filenames

Place LoRA files in `apps/ai-backend/cache/lora/`:

| Camera Style | Expected Filename | Weight |
|--------------|------------------|--------|
| Hasselblad X2D | `c41_hasselblad_portra400.safetensors` | 1.0 |
| Leica M Series | `leica_m_style.safetensors` | 0.9 |
| Zeiss Otus | `zeiss_otus_style.safetensors` | 0.95 |
| Fujifilm GFX | `fujifilm_gfx_style.safetensors` | 1.0 |

## Installation Steps

### 1. Create Cache Directory

```bash
cd apps/ai-backend
mkdir -p cache/lora
```

### 2. Download LoRA Files

Option A: Using the download script (if repos are configured)
```bash
python scripts/download_models.py --lora --style hasselblad
```

Option B: Manual download
```bash
# Download from Civitai or HuggingFace
# Copy to cache/lora/ directory
cp ~/Downloads/hasselblad_lora.safetensors cache/lora/c41_hasselblad_portra400.safetensors
```

### 3. Verify Files

```bash
ls -lh cache/lora/
# Expected output:
# c41_hasselblad_portra400.safetensors
# leica_m_style.safetensors
# zeiss_otus_style.safetensors
# fujifilm_gfx_style.safetensors
```

## Configuration

### Update `apps/ai-backend/services/model_loader.py`

The LoRA configuration is in the `_load_lora_weights()` method:

```python
lora_configs = {
    CameraStyle.HASSELBLAD: (
        "c41_hasselblad_portra400.safetensors",
        1.0,  # Weight strength
    ),
    CameraStyle.LEICA_M: (
        "leica_m_style.safetensors",
        0.9,
    ),
    CameraStyle.ZEISS: (
        "zeiss_otus_style.safetensors",
        0.95,
    ),
    CameraStyle.FUJIFILM_GFX: (
        "fujifilm_gfx_style.safetensors",
        1.0,
    ),
}
```

## Testing

### Test Single Style

```bash
cd apps/ai-backend
python -c "
from services.model_loader import model_loader
from models.enums import CameraStyle

model_loader.load_model()
model_loader.apply_lora_style(CameraStyle.HASSELBLAD)
print('LoRA loaded successfully!')
"
```

### Test All Styles

```bash
# Start the backend
uvicorn api.main:app --reload

# In another terminal, test each style
curl -X POST http://localhost:8000/api/v1/transform \
  -F "image=@test_photo.jpg" \
  -F "style=hasselblad"

curl -X POST http://localhost:8000/api/v1/transform \
  -F "image=@test_photo.jpg" \
  -F "style=leica_m"
```

## Troubleshooting

### LoRA File Not Found

**Error**: `LoRA file not found: .../cache/lora/xxx.safetensors`

**Solution**:
1. Verify file exists: `ls apps/ai-backend/cache/lora/`
2. Check filename matches exactly (case-sensitive)
3. Verify directory is not gitignored

### LoRA Not Applying Style

**Possible causes**:
1. LoRA not FLUX.1-Schnell compatible
2. Weight too low (try increasing to 1.2)
3. LoRA needs higher denoising strength

**Solution**: Edit `image_service.py`:
```python
DEFAULT_DENOISING_STRENGTH = 0.4  # Increase from 0.35
```

### Out of Memory

**Error**: `CUDA out of memory`

**Solutions**:
1. Reduce image resolution (use `preview` mode)
2. Unload unused LoRas before loading new one
3. Reduce batch size

## Production Deployment

For production, consider:

1. **Pre-download LoRAs** during Docker build
2. **Store in R2** for multi-instance deployments
3. **Version LoRAs** (e.g., `hasselblad_v1.safetensors`)
4. **A/B test** different LoRA weights

### Docker Build with LoRAs

```dockerfile
# In apps/ai-backend/Dockerfile
COPY cache/lora/*.safetensors /app/cache/lora/
```

## References

- FLUX.1 LoRA Training: https://huggingface.co/docs/diffusers/training/lora
- Civitai LoRA Guide: https://civitai.com/articles/4096
- FLUX.1 Models: https://huggingface.co/black-forest-labs/FLUX.1-schnell
