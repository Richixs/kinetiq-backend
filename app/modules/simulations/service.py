"""Business logic for rendering kinematics simulations with Manim."""

from __future__ import annotations

import shutil
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path

from manim import tempconfig

from app.modules.simulations.models import SimulationRequest
from app.modules.simulations.scenes.mru_scene import MRUScene


# Manim's config is global state. Parallel renders would step on each other,
# so we serialize them with a module-level lock. Acceptable for an academic
# demo — renders are short and concurrent users are few.
_render_lock = threading.Lock()


@dataclass
class RenderResult:
    """Output of a successful Manim render."""

    video_path: Path
    _workdir: Path

    def cleanup(self) -> None:
        """Remove the temporary render directory."""
        shutil.rmtree(self._workdir, ignore_errors=True)


# pylint: disable=too-few-public-methods
class SimulationService:
    """Render a SimulationRequest to an MP4 using Manim."""

    def render(self, request: SimulationRequest) -> RenderResult:
        """Run the Manim scene and return the path to the resulting video."""
        workdir = Path(tempfile.mkdtemp(prefix="kinetiq_"))

        overrides = {
            "quality": "low_quality",  # 480p15 per v1 spec
            "media_dir": str(workdir),
            "disable_caching": True,
            "output_file": "mru",
        }

        with _render_lock, tempconfig(overrides):
            scene = MRUScene(t_max=request.t_max, moviles=request.moviles)
            scene.render()
            video_path = Path(scene.renderer.file_writer.movie_file_path)

        return RenderResult(video_path=video_path, _workdir=workdir)
