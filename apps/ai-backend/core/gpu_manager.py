"""
GPU memory management for Hasselize AI Backend.

Manages GPU memory allocation and optimization for RTX 5090.
Implements memory-efficient loading and inference strategies.
"""

import gc
import logging
from contextlib import contextmanager

import torch

from .config import settings

logger = logging.getLogger(__name__)


class GPUManager:
    """
    GPU memory management utilities.

    Features:
    - Memory usage monitoring
    - Automatic cleanup and garbage collection
    - Memory fraction control
    - Device management for multi-GPU setups
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern for GPU manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize GPU manager with settings."""
        if self._initialized:
            return

        self._initialized = True
        self.device = self._get_device()
        self._setup_memory()

    def _get_device(self) -> torch.device:
        """
        Get the appropriate device for computation.

        Returns CUDA device if available, otherwise CPU.
        """
        if torch.cuda.is_available():
            device_id = settings.cuda_visible_devices
            device = torch.device(f"cuda:{device_id}")
            logger.info(f"Using CUDA device: {device}")
            return device
        logger.warning("CUDA not available, using CPU")
        return torch.device("cpu")

    def _setup_memory(self):
        """Configure GPU memory settings."""
        if not self.is_cuda_available:
            return

        # Enable memory efficiency options
        try:
            # Set memory fraction if specified
            if settings.gpu_memory_fraction < 1.0:
                torch.cuda.set_per_process_memory_fraction(
                    settings.gpu_memory_fraction,
                    device=self.device,
                )
                logger.info(
                    f"GPU memory fraction set to {settings.gpu_memory_fraction}"
                )
        except Exception as e:
            logger.warning(f"Could not set GPU memory fraction: {e}")

    @property
    def is_cuda_available(self) -> bool:
        """Check if CUDA is available."""
        return torch.cuda.is_available()

    @property
    def device_name(self) -> str:
        """Get the device name."""
        if self.is_cuda_available:
            return torch.cuda.get_device_name(self.device)
        return "CPU"

    @property
    def memory_used_mb(self) -> int | None:
        """Get current GPU memory usage in MB."""
        if not self.is_cuda_available:
            return None
        return torch.cuda.memory_allocated(self.device) // (1024 * 1024)

    @property
    def memory_reserved_mb(self) -> int | None:
        """Get current GPU memory reservation in MB."""
        if not self.is_cuda_available:
            return None
        return torch.cuda.memory_reserved(self.device) // (1024 * 1024)

    @property
    def memory_total_mb(self) -> int | None:
        """Get total GPU memory in MB."""
        if not self.is_cuda_available:
            return None
        return torch.cuda.get_device_properties(self.device).total_memory // (
            1024 * 1024
        )

    @property
    def memory_free_mb(self) -> int | None:
        """Get free GPU memory in MB."""
        if not self.is_cuda_available:
            return None
        total = self.memory_total_mb or 0
        used = self.memory_used_mb or 0
        return total - used

    def get_memory_stats(self) -> dict[str, int | str | bool]:
        """
        Get comprehensive memory statistics.

        Returns:
            Dictionary with memory stats for health checks.
        """
        return {
            "gpu_available": self.is_cuda_available,
            "device_name": self.device_name,
            "memory_used_mb": self.memory_used_mb,
            "memory_reserved_mb": self.memory_reserved_mb,
            "memory_total_mb": self.memory_total_mb,
            "memory_free_mb": self.memory_free_mb,
        }

    def cleanup(self):
        """
        Force cleanup of GPU memory.

        Clears cache and runs garbage collection.
        Use sparingly as it can impact performance.
        """
        if self.is_cuda_available:
            torch.cuda.empty_cache()
            gc.collect()
            logger.debug("GPU memory cleaned up")

    @contextmanager
    def memory_context(self, cleanup: bool = True):
        """
        Context manager for GPU memory management.

        Args:
            cleanup: Whether to force cleanup after context exit.

        Example:
            with gpu_manager.memory_context():
                model.load()
                result = model.generate()
        """
        initial_memory = self.memory_used_mb
        try:
            yield self
        finally:
            if cleanup and self.is_cuda_available:
                self.cleanup()
            final_memory = self.memory_used_mb
            logger.debug(
                f"Memory context: {initial_memory}MB -> {final_memory}MB "
                f"(delta: {final_memory - initial_memory:+d}MB)"
            )


# Global GPU manager instance
gpu_manager = GPUManager()
