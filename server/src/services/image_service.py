"""
Serviço de geração de imagens usando Stability AI.
Gera imagens a partir de texto considerando diretrizes visuais da persona.
"""

from typing import Dict, Any, Optional, Tuple
import os
import uuid
import base64
from pathlib import Path
from datetime import datetime
import logging

import httpx
from PIL import Image
from io import BytesIO

from ..core.config import settings

logger = logging.getLogger(__name__)


class ImageService:
    """
    Text-to-Image com Stability AI (SDXL 1024)

    - Usa httpx (já no requirements) para chamadas REST
    - Salva a imagem em /uploads/images e retorna URL relativa servida pelo FastAPI StaticFiles
    """

    def __init__(self):
        self.api_key = settings.STABILITY_API_KEY
        self.base_url = "https://api.stability.ai"
        self.model = "stable-diffusion-xl-1024-v1-0"  # modelo estável e acessível
        # Diretório de saída
        self.output_dir = Path("uploads") / "images"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_api_key(self):
        if not self.api_key:
            raise ValueError(
                "STABILITY_API_KEY não configurada. Defina no arquivo .env para gerar imagens."
            )

    def _build_style_prompt(self, persona_data: Dict[str, Any]) -> str:
        """Cria um trecho de prompt com base nas diretrizes visuais da persona."""
        vg = (persona_data or {}).get("visual_guidelines", {}) or {}
        parts = []
        image_style = vg.get("image_style")
        if image_style:
            parts.append(image_style)
        primary_colors = vg.get("primary_colors") or []
        if primary_colors:
            parts.append("palette: " + ", ".join(primary_colors[:3]))
        fonts = vg.get("fonts") or []
        if fonts:
            parts.append("typography influence: " + ", ".join(fonts[:2]))
        brand_elements = vg.get("brand_elements") or []
        if brand_elements:
            parts.append("brand elements: " + ", ".join(brand_elements[:3]))
        # fallback leve
        if not parts:
            parts.append("clean, modern, instagram aesthetic")
        return ", ".join(parts)

    def _size_from_ratio(self, ratio: str) -> Tuple[int, int]:
        ratio = (ratio or "square").lower()
        if ratio in ("square", "1:1"):
            return 1024, 1024
        if ratio in ("portrait", "4:5"):
            return 832, 1024  # aproximadamente 4:5
        if ratio in ("landscape", "16:9"):
            return 1216, 704  # próximo a 16:9 mantendo limites do modelo
        return 1024, 1024

    async def generate_image(
        self,
        persona_data: Dict[str, Any],
        prompt: str,
        ratio: str = "square",
        negative_prompt: Optional[str] = None,
        cfg_scale: float = 7.0,
        steps: int = 30,
        seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        self._ensure_api_key()

        style_prompt = self._build_style_prompt(persona_data)
        full_prompt = f"{prompt}. Style: {style_prompt}. Highly detailed, professional, photorealistic, instagram ready."
        width, height = self._size_from_ratio(ratio)

        url = f"{self.base_url}/v1/generation/{self.model}/text-to-image"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        payload = {
            "text_prompts": [
                {"text": full_prompt, "weight": 1},
            ]
        }
        if negative_prompt:
            payload["text_prompts"].append({"text": negative_prompt, "weight": -1})

        payload.update(
            {
                "cfg_scale": cfg_scale,
                "height": height,
                "width": width,
                "samples": 1,
                "steps": steps,
            }
        )
        if seed is not None:
            payload["seed"] = seed

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                logger.error(f"Stability API error {resp.status_code}: {resp.text}")
                raise ValueError("Falha ao gerar imagem na API de imagens.")
            data = resp.json()

        artifacts = data.get("artifacts") or []
        if not artifacts:
            raise ValueError("API de imagens não retornou resultados.")

        image_b64 = artifacts[0].get("base64")
        if not image_b64:
            raise ValueError("Resposta de imagem inválida.")

        # Salvar arquivo
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        filename = f"img_{uuid.uuid4().hex}.png"
        filepath = self.output_dir / filename
        image.save(filepath, format="PNG")

        logger.info(
            f"🖼️ Imagem gerada e salva em {filepath} ({width}x{height})"
        )

        return {
            "url": f"/uploads/images/{filename}",
            "path": str(filepath),
            "width": width,
            "height": height,
            "prompt": prompt,
            "style_prompt": style_prompt,
            "generated_at": datetime.utcnow().isoformat(),
            "model": self.model,
        }


# Instância global
image_service = ImageService()
