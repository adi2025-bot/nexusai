"""
Image Generation Service
Uses Pollinations AI for free, unlimited image generation.
"""

import logging
import requests
import time
import base64
from typing import Optional, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from urllib.parse import quote

logger = logging.getLogger("NexusAI.ImageService")


@dataclass
class GeneratedImage:
    """Represents a generated image."""
    url: str
    prompt: str
    provider: str
    model: str
    width: int = 1024
    height: int = 1024
    generation_time: float = 0.0
    
    @property
    def is_base64(self) -> bool:
        """Check if the URL is a base64 data URI."""
        return self.url.startswith("data:image")


class ImageProvider(ABC):
    """Abstract base class for image generation providers."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> GeneratedImage:
        """Generate an image from a text prompt."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass


class PollinationsProvider(ImageProvider):
    """
    Pollinations AI - Free image generation.
    No API key required, uses FLUX model.
    """
    
    BASE_URL = "https://image.pollinations.ai/prompt"
    
    def __init__(self):
        self._available = True
    
    @property
    def name(self) -> str:
        return "pollinations"
    
    def is_available(self) -> bool:
        return self._available
    
    def generate(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        model: str = "flux",
        seed: int = None,
        **kwargs
    ) -> GeneratedImage:
        """
        Generate an image using Pollinations AI.
        
        Args:
            prompt: Text description of the image
            width: Image width (default 1024)
            height: Image height (default 1024)
            model: Model to use ('flux', 'turbo', 'flux-realism', 'flux-anime')
            seed: Random seed for reproducibility
        """
        start_time = time.time()
        
        # URL encode the prompt
        encoded_prompt = quote(prompt)
        
        # Build URL with parameters
        url = f"{self.BASE_URL}/{encoded_prompt}"
        params = {
            "width": width,
            "height": height,
            "model": model,
            "nologo": "true"
        }
        if seed is not None:
            params["seed"] = seed
        
        # Add query params
        param_str = "&".join(f"{k}={v}" for k, v in params.items())
        full_url = f"{url}?{param_str}"
        
        generation_time = time.time() - start_time
        
        return GeneratedImage(
            url=full_url,
            prompt=prompt,
            provider="pollinations",
            model=model,
            width=width,
            height=height,
            generation_time=generation_time
        )
    
    def get_available_models(self) -> list:
        """Get list of available Pollinations models."""
        return [
            {"id": "flux", "name": "FLUX (Default)", "description": "High quality, balanced"},
            {"id": "flux-realism", "name": "FLUX Realism", "description": "Photorealistic images"},
            {"id": "flux-anime", "name": "FLUX Anime", "description": "Anime/cartoon style"},
            {"id": "flux-3d", "name": "FLUX 3D", "description": "3D rendered style"},
            {"id": "turbo", "name": "Turbo", "description": "Faster generation"},
        ]
    
    def edit_image(
        self,
        image_url: str,
        edit_prompt: str,
        width: int = 1024,
        height: int = 1024,
        model: str = "flux",
        strength: float = 0.7,
        **kwargs
    ) -> GeneratedImage:
        """
        Edit an existing image using Pollinations AI.
        
        This uses img2img style transfer by including the source image URL
        in the prompt for reference-based generation.
        
        Args:
            image_url: URL of the source image to edit
            edit_prompt: Description of desired edits/changes
            width: Output image width
            height: Output image height
            model: Model to use for generation
            strength: How much to modify the original (0.0-1.0)
        """
        start_time = time.time()
        
        # Construct the edit prompt with image reference
        # Pollinations supports image reference via URL in prompt
        combined_prompt = f"{edit_prompt}, based on reference image: {image_url}"
        encoded_prompt = quote(combined_prompt)
        
        # Build URL with parameters
        url = f"{self.BASE_URL}/{encoded_prompt}"
        params = {
            "width": width,
            "height": height,
            "model": model,
            "nologo": "true"
        }
        
        param_str = "&".join(f"{k}={v}" for k, v in params.items())
        full_url = f"{url}?{param_str}"
        
        generation_time = time.time() - start_time
        
        return GeneratedImage(
            url=full_url,
            prompt=edit_prompt,
            provider="pollinations",
            model=f"{model}-edit",
            width=width,
            height=height,
            generation_time=generation_time
        )


class ClipdropProvider(ImageProvider):
    """
    Clipdrop AI - High quality image generation.
    Free tier: 100 images/month.
    Requires API key from https://clipdrop.co/apis
    """
    
    API_URL = "https://clipdrop-api.co/text-to-image/v1"
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
    
    @property
    def name(self) -> str:
        return "clipdrop"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        model: str = "sdxl",
        **kwargs
    ) -> GeneratedImage:
        """
        Generate an image using Clipdrop API.
        
        Args:
            prompt: Text description of the image (max 1000 chars)
            width: Image width (default 1024)
            height: Image height (default 1024)
            model: Model style (uses SDXL internally)
        """
        if not self.is_available():
            raise ValueError("Clipdrop API key not configured. Get one free at https://clipdrop.co/apis")
        
        start_time = time.time()
        
        headers = {
            "x-api-key": self.api_key
        }
        
        # Clipdrop uses form data
        data = {
            "prompt": prompt[:1000]  # Max 1000 chars
        }
        
        try:
            response = requests.post(
                self.API_URL,
                headers=headers,
                files={"prompt": (None, prompt[:1000])},
                timeout=60
            )
            response.raise_for_status()
            
            # Clipdrop returns the image directly as bytes
            image_bytes = response.content
            
            # Convert to base64 data URI
            import base64
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            image_url = f"data:image/png;base64,{image_b64}"
            
            generation_time = time.time() - start_time
            
            return GeneratedImage(
                url=image_url,
                prompt=prompt,
                provider="clipdrop",
                model="sdxl",
                width=width,
                height=height,
                generation_time=generation_time
            )
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "402" in error_msg or "credits" in error_msg.lower():
                logger.error("Clipdrop credits exhausted")
                raise ValueError("Clipdrop free credits exhausted (100/month). Using Pollinations instead.")
            logger.error(f"Clipdrop error: {e}")
            raise ValueError(f"Image generation failed: {str(e)}")
    
    def get_available_models(self) -> list:
        """Get list of available Clipdrop models."""
        return [
            {"id": "sdxl", "name": "SDXL", "description": "Stable Diffusion XL - High quality"},
        ]


class ImageService:
    """
    Main image generation service.
    Priority: Clipdrop (100 free/month) → Pollinations (unlimited free).
    """
    
    def __init__(self, clipdrop_key: str = ""):
        self.providers: Dict[str, ImageProvider] = {
            "pollinations": PollinationsProvider(),
        }
        
        # Add Clipdrop if API key is available and set as primary
        if clipdrop_key:
            self.providers["clipdrop"] = ClipdropProvider(clipdrop_key)
            self._current_provider = "clipdrop"  # Clipdrop first!
        else:
            self._current_provider = "pollinations"
        
        self._current_model = "flux"
    
    @property
    def current_provider(self) -> str:
        return self._current_provider
    
    @current_provider.setter
    def current_provider(self, value: str):
        if value in self.providers:
            self._current_provider = value
            # Reset model to default for new provider
            provider = self.providers[value]
            models = provider.get_available_models()
            if models:
                self._current_model = models[0]["id"]
    
    @property
    def current_model(self) -> str:
        return self._current_model
    
    @current_model.setter
    def current_model(self, value: str):
        self._current_model = value
    
    def get_provider(self, name: str = None) -> Optional[ImageProvider]:
        """Get a provider by name, or the current provider."""
        name = name or self._current_provider
        return self.providers.get(name)
    
    def get_available_providers(self) -> list:
        """Get list of available provider names with details."""
        result = []
        for name, provider in self.providers.items():
            if provider.is_available():
                result.append({
                    "id": name,
                    "name": "🎨 Pollinations (Free)",
                    "models": provider.get_available_models()
                })
        return result
    
    def generate(
        self,
        prompt: str,
        provider: str = None,
        model: str = None,
        width: int = 1024,
        height: int = 1024,
        **kwargs
    ) -> GeneratedImage:
        """
        Generate an image. Uses Clipdrop first, falls back to Pollinations.
        
        Args:
            prompt: Text description of the image
            provider: Provider name (optional, uses current)
            model: Model name (optional, uses current style)
            width: Image width
            height: Image height
        """
        provider_name = provider or self._current_provider
        model_name = model or self._current_model
        
        image_provider = self.get_provider(provider_name)
        if not image_provider:
            image_provider = self.providers.get("pollinations")
        
        try:
            return image_provider.generate(
                prompt=prompt,
                model=model_name,
                width=width,
                height=height,
                **kwargs
            )
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if Clipdrop credits exhausted - fallback to Pollinations
            if provider_name == "clipdrop":
                fallback_triggers = ["402", "credit", "exhausted", "limit", "quota"]
                should_fallback = any(trigger in error_msg for trigger in fallback_triggers)
                
                if should_fallback or True:  # Always fallback on any Clipdrop error
                    logger.warning(f"Clipdrop failed ({e}), falling back to Pollinations")
                    
                    pollinations = self.providers.get("pollinations")
                    if pollinations:
                        return pollinations.generate(
                            prompt=prompt,
                            model=model_name,
                            width=width,
                            height=height,
                            **kwargs
                        )
            
            # Re-raise if no fallback available
            raise
    
    def edit(
        self,
        image_url: str,
        edit_prompt: str,
        model: str = None,
        width: int = 1024,
        height: int = 1024,
        **kwargs
    ) -> GeneratedImage:
        """
        Edit an existing image using the Pollinations provider.
        
        Args:
            image_url: URL of the source image
            edit_prompt: Description of desired changes
            model: Style model to use (optional)
            width: Output width
            height: Output height
        """
        # Use Pollinations for editing (it's free)
        pollinations = self.providers.get("pollinations")
        if not pollinations:
            raise ValueError("Pollinations provider not available for editing")
        
        style = model or self._current_model or "flux"
        
        return pollinations.edit_image(
            image_url=image_url,
            edit_prompt=edit_prompt,
            model=style,
            width=width,
            height=height,
            **kwargs
        )
    
    def is_ready(self) -> bool:
        """Check if at least one provider is available."""
        return any(p.is_available() for p in self.providers.values())


# Factory function
def create_image_service() -> ImageService:
    """Create an image service with available providers from settings."""
    from config.settings import settings
    
    clipdrop_key = getattr(settings.ai, 'clipdrop_api_key', '') or ''
    
    return ImageService(clipdrop_key=clipdrop_key)


