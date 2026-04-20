"""Manim scene for 1D kinematics with multiple móviles.

Handles MRU and MRUV uniformly via the general formula
`x(t) = x₀ + v·Δt + ½·a·Δt²`; MRU is the `a == 0` special case.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Sequence

from manim import (
    BOLD,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    UR,
    WHITE,
    Arrow,
    Axes,
    Dot,
    ManimColor,
    Mobject,
    NumberLine,
    Scene,
    Text,
    VGroup,
    VMobject,
    ValueTracker,
    always_redraw,
    linear,
)

if TYPE_CHECKING:
    from app.modules.simulations.models import Movil


# ---------------------------------------------------------------------------
# Layout / style constants (Manim camera is 14.2 × 8 in scene units)
# ---------------------------------------------------------------------------

ANIMATION_DURATION: float = 15.0  # wall-clock seconds per render, fixed

NUMBER_LINE_LENGTH = 11
NUMBER_LINE_Y = 1.1
GRAPH_X_OFFSET = 3.6
GRAPH_Y = -2.3
GRAPH_X_LENGTH = 5.2
GRAPH_Y_LENGTH = 2.6

DOT_RADIUS = 0.14
ARROW_STROKE = 6
ARROW_UNIT_LENGTH = 1.2  # max |v| maps to this many scene units
TRACE_STROKE = 3

TITLE_FONT = 28
TIME_FONT = 22
MOVIL_LETTER_FONT = 24
POS_LABEL_FONT = 16
AXIS_LABEL_FONT = 16
AXIS_NUMBER_FONT = 16
NUMBER_LINE_FONT = 20

# Per-móvil vertical stacking so labels don't collide during encounters.
LABEL_BUFF_BASE = 0.18
LABEL_BUFF_STEP = 0.32
POS_BUFF_BASE = 0.50
POS_BUFF_STEP = 0.28

X_RANGE_MARGIN = 0.10
V_RANGE_MARGIN = 0.20


@dataclass
class MovilVisuals:
    """Per-móvil render-time context, built once at setup."""

    movil: "Movil"
    color: ManimColor
    label_buff: float
    pos_buff: float
    arrow_scale: float


class MRUScene(Scene):
    """Parametrized 1D kinematics scene (MRU + MRUV) with multiple moviles."""

    def __init__(
        self,
        t_max: float,
        moviles: Sequence["Movil"],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.t_max = float(t_max)
        self.moviles = list(moviles)
        self.t_tracker = ValueTracker(0.0)
        self.number_line: NumberLine | None = None

    # ------------------------------------------------------------------ #
    # Physics — MRUV general form; MRU is the a == 0 special case.       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _x_of_t(m: "Movil", t: float) -> float:
        if t <= m.t_start:
            return m.x_0
        dt = t - m.t_start
        return m.x_0 + m.v * dt + 0.5 * m.a * dt * dt

    @staticmethod
    def _v_of_t(m: "Movil", t: float) -> float:
        if t <= m.t_start:
            return 0.0
        return m.v + m.a * (t - m.t_start)

    # ------------------ #
    # Auto-scale helpers #
    # ------------------ #

    def _compute_x_range(self) -> tuple[float, float]:
        positions = [m.x_0 for m in self.moviles] + [
            self._x_of_t(m, self.t_max) for m in self.moviles
        ]
        lo, hi = min(positions), max(positions)
        margin = max((hi - lo) * X_RANGE_MARGIN, 1.0)
        return lo - margin, hi + margin

    def _compute_v_range(self) -> tuple[float, float]:
        velocities = [0.0]
        for m in self.moviles:
            velocities.append(m.v)
            velocities.append(self._v_of_t(m, self.t_max))
        lo, hi = min(velocities), max(velocities)
        margin = max((hi - lo) * V_RANGE_MARGIN, 1.0)
        return lo - margin, hi + margin

    @staticmethod
    def _nice_step(total: float, target_ticks: int) -> float:
        """Return a 1/2/5-style tick step for the given span and target tick count."""
        if total <= 0 or target_ticks <= 0:
            return 1.0
        rough = total / target_ticks
        power = 10 ** math.floor(math.log10(rough))
        normalized = rough / power
        if normalized < 1.5:
            return 1 * power
        if normalized < 3:
            return 2 * power
        if normalized < 7:
            return 5 * power
        return 10 * power

    def _make_visuals(self) -> list[MovilVisuals]:
        # Pick arrow scale from the peak |v| reached across the simulation,
        # not just the initial |v|. For MRUV v(t) is linear in t, so the
        # extremum sits at one of the endpoints (t_start or t_max).
        peak_v_abs = max(
            (
                max(abs(m.v), abs(self._v_of_t(m, self.t_max)))
                for m in self.moviles
            ),
            default=1.0,
        ) or 1.0
        return [
            MovilVisuals(
                movil=m,
                color=ManimColor(m.color),
                label_buff=LABEL_BUFF_BASE + idx * LABEL_BUFF_STEP,
                pos_buff=POS_BUFF_BASE + idx * POS_BUFF_STEP,
                arrow_scale=ARROW_UNIT_LENGTH / peak_v_abs,
            )
            for idx, m in enumerate(self.moviles)
        ]

    # --------------- #
    # Scene assembly  #
    # --------------- #

    def construct(self) -> None:  # pragma: no cover — rendered by Manim
        visuals = self._make_visuals()
        x_range = self._compute_x_range()
        v_range = self._compute_v_range()

        self._add_title()
        self._add_time_hud()
        self._add_number_line(x_range)
        self._add_moviles(visuals)
        self._add_graph(
            position=LEFT * GRAPH_X_OFFSET + UP * GRAPH_Y,
            y_range=x_range,
            y_label="x (m)",
            visuals=visuals,
            segments_for=self._x_trace_segments,
        )
        self._add_graph(
            position=RIGHT * GRAPH_X_OFFSET + UP * GRAPH_Y,
            y_range=v_range,
            y_label="v (m/s)",
            visuals=visuals,
            segments_for=self._v_trace_segments,
        )

        self.play(
            self.t_tracker.animate.set_value(self.t_max),
            run_time=ANIMATION_DURATION,
            rate_func=linear,
        )
        self.wait(0.5)

    def _add_title(self) -> None:
        self.add(
            Text("Simulación de cinemática", font_size=TITLE_FONT, color=WHITE).to_edge(
                UP, buff=0.25
            )
        )

    def _add_time_hud(self) -> None:
        self.add(
            always_redraw(
                lambda: Text(
                    f"t = {self.t_tracker.get_value():.2f} s",
                    font_size=TIME_FONT,
                ).to_corner(UR, buff=0.4)
            )
        )

    def _add_number_line(self, x_range: tuple[float, float]) -> None:
        x_min, x_max = x_range
        self.number_line = NumberLine(
            x_range=[x_min, x_max, self._nice_step(x_max - x_min, 10)],
            length=NUMBER_LINE_LENGTH,
            include_numbers=True,
            include_tip=True,
            font_size=NUMBER_LINE_FONT,
            decimal_number_config={"num_decimal_places": 0},
        ).shift(UP * NUMBER_LINE_Y)
        x_axis_label = Text("x (m)", font_size=20).next_to(
            self.number_line.get_end(), UP * 0.4 + RIGHT * 0.15
        )
        self.add(self.number_line, x_axis_label)

    def _add_moviles(self, visuals: list[MovilVisuals]) -> None:
        # One always_redraw per móvil returning a VGroup. This evaluates
        # x(t) and n2p() once per frame instead of once per sub-mobject.
        for v in visuals:
            self.add(always_redraw(lambda v=v: self._movil_frame(v)))

    def _movil_frame(self, v: MovilVisuals) -> VGroup:
        assert self.number_line is not None
        t = self.t_tracker.get_value()
        x = self._x_of_t(v.movil, t)
        point = self.number_line.n2p(x)
        v_now = self._v_of_t(v.movil, t)

        dot = Dot(point, color=v.color, radius=DOT_RADIUS)
        letter = Text(
            v.movil.label,
            font_size=MOVIL_LETTER_FONT,
            color=v.color,
            weight=BOLD,
        ).next_to(point, UP, buff=v.label_buff)
        pos_value = Text(
            f"{x:.1f}",
            font_size=POS_LABEL_FONT,
            color=v.color,
        ).next_to(point, DOWN, buff=v.pos_buff)

        if abs(v_now) < 1e-6:
            # Zero-length arrows crash Manim — render nothing instead.
            arrow: Mobject = VMobject()
        else:
            arrow = Arrow(
                start=point,
                end=point + RIGHT * v_now * v.arrow_scale,
                buff=0,
                color=v.color,
                stroke_width=ARROW_STROKE,
                max_tip_length_to_length_ratio=0.3,
                max_stroke_width_to_length_ratio=8,
            )

        return VGroup(dot, letter, arrow, pos_value)

    def _add_graph(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        position,
        y_range: tuple[float, float],
        y_label: str,
        visuals: list[MovilVisuals],
        segments_for: Callable[[MovilVisuals, Axes], list[Mobject]],
    ) -> None:
        y_min, y_max = y_range
        axes = Axes(
            x_range=[0, self.t_max, self._nice_step(self.t_max, 5)],
            y_range=[y_min, y_max, self._nice_step(y_max - y_min, 5)],
            x_length=GRAPH_X_LENGTH,
            y_length=GRAPH_Y_LENGTH,
            tips=False,
            axis_config={"include_numbers": True, "font_size": AXIS_NUMBER_FONT},
        ).move_to(position)
        labels = axes.get_axis_labels(
            Text("t (s)", font_size=AXIS_LABEL_FONT),
            Text(y_label, font_size=AXIS_LABEL_FONT),
        )
        self.add(axes, labels)

        for v in visuals:
            for segment in segments_for(v, axes):
                self.add(segment)

    def _x_trace_segments(self, v: MovilVisuals, axes: Axes) -> list[Mobject]:
        # x(t) is continuous at t_start — one segment spans the full range.
        return [
            self._progressive_segment(
                axes,
                lambda t, m=v.movil: self._x_of_t(m, t),
                v.color,
                0.0,
                self.t_max,
            )
        ]

    def _v_trace_segments(self, v: MovilVisuals, axes: Axes) -> list[Mobject]:
        # v(t) has a step discontinuity at t_start. We plot the pre-start
        # flat-at-zero piece and the post-start velocity piece as separate
        # mobjects so `plot()`'s sampling doesn't bridge the jump with a
        # slanted line.
        segments: list[Mobject] = []
        if v.movil.t_start > 0:
            segments.append(
                self._progressive_segment(
                    axes,
                    lambda t: 0.0,
                    v.color,
                    0.0,
                    v.movil.t_start,
                )
            )
        segments.append(
            self._progressive_segment(
                axes,
                lambda t, m=v.movil: self._v_of_t(m, t),
                v.color,
                v.movil.t_start,
                self.t_max,
            )
        )
        return segments

    def _progressive_segment(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        axes: Axes,
        func: Callable[[float], float],
        color: ManimColor,
        t_start: float,
        t_end: float,
    ) -> Mobject:
        """Return a mobject that progressively reveals a curve from `t_start`
        to `t_end` as the time tracker advances."""

        def trace_up_to_now() -> Mobject:
            t_now = self.t_tracker.get_value()
            draw_end = min(t_now, t_end)
            if draw_end - t_start < 1e-3:
                return VMobject()
            return axes.plot(
                func,
                x_range=[t_start, draw_end],
                color=color,
                stroke_width=TRACE_STROKE,
            )

        return always_redraw(trace_up_to_now)
