"""Pydantic models for the kinematics simulation module.

Supports both MRU and MRUV uniformly: the `a` (acceleration) field on
`Movil` defaults to 0 (pure MRU), and any nonzero value makes it MRUV.
"""

from typing import List

from pydantic import BaseModel, Field, model_validator


class Movil(BaseModel):
    """A single moving point on the 1D axis."""

    label: str = Field(
        ...,
        min_length=1,
        max_length=4,
        description="Nombre corto del móvil (ej: 'A', 'B', 'C').",
    )
    x_0: float = Field(..., description="Posición inicial en metros.")
    v: float = Field(..., description="Velocidad en m/s (con signo para dirección).")
    t_start: float = Field(
        0.0,
        ge=0,
        description="Instante en que el móvil empieza a moverse (s).",
    )
    color: str = Field(
        "#e74c3c",
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="Color hex #RRGGBB para distinguir el móvil en la escena.",
    )
    a: float = Field(
        0.0,
        description="Aceleración en m/s² (default 0 = MRU, distinto de 0 = MRUV).",
    )


class SimulationRequest(BaseModel):
    """Input payload for rendering a kinematics simulation."""

    t_max: float = Field(
        ...,
        gt=0,
        description="Tiempo físico total a simular (s).",
    )
    moviles: List[Movil] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="Lista de móviles (máximo 3 en v1).",
    )

    @model_validator(mode="after")
    def _validate_t_start_vs_t_max(self) -> "SimulationRequest":
        for m in self.moviles:
            if m.t_start >= self.t_max:
                raise ValueError(
                    f"t_start del móvil '{m.label}' ({m.t_start}) "
                    f"debe ser menor que t_max ({self.t_max})."
                )
        return self
