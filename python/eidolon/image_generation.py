from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

import torch
from diffusers import AutoPipelineForText2Image

from eidolon.core.config import DATA_DIR


class ImageGenerationService:
    def __init__(self, model_id: str = 'segmind/tiny-sd') -> None:
        self.model_id = model_id
        self._pipeline = None
        self._loaded_model_id = ''
        self._artifacts_dir = DATA_DIR / 'generated'
        self._artifacts_dir.mkdir(parents=True, exist_ok=True)

    def is_available(self) -> tuple[bool, str]:
        try:
            import diffusers  # noqa: F401
            import transformers  # noqa: F401
            return True, f'Realer lokaler Bildpfad aktiv ({self.model_id})'
        except Exception as exc:
            return False, f'Bildpfad nicht startbar: {exc}'

    def generate(self, prompt: str, *, negative_prompt: str = '', steps: int = 2, guidance_scale: float = 7.5, width: int = 512, height: int = 512, seed: int | None = None, model_id: str | None = None) -> dict[str, Any]:
        chosen_model = model_id or self.model_id
        pipe = self._get_pipeline(chosen_model)
        generator = None
        if seed is not None:
            generator = torch.Generator(device='cpu').manual_seed(int(seed))
        image = pipe(prompt=prompt, negative_prompt=negative_prompt or None, num_inference_steps=int(steps), guidance_scale=float(guidance_scale), width=int(width), height=int(height), generator=generator).images[0]
        digest = hashlib.sha1(f'{prompt}|{time.time()}'.encode('utf-8')).hexdigest()[:12]
        out = self._artifacts_dir / f'image_{digest}.png'
        image.save(out)
        return {
            'ok': True,
            'path': str(out),
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'model_id': chosen_model,
            'steps': int(steps),
            'guidance_scale': float(guidance_scale),
            'width': image.width,
            'height': image.height,
            'seed': seed,
        }

    def _get_pipeline(self, model_id: str):
        if self._pipeline is not None and self._loaded_model_id == model_id:
            return self._pipeline
        pipe = AutoPipelineForText2Image.from_pretrained(model_id, safety_checker=None, torch_dtype=torch.float32)
        pipe = pipe.to('cpu')
        self._pipeline = pipe
        self._loaded_model_id = model_id
        return pipe


_service: ImageGenerationService | None = None


def get_image_generation_service() -> ImageGenerationService:
    global _service
    if _service is None:
        _service = ImageGenerationService()
    return _service
