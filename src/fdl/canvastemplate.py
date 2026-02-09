from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, Literal, Union

from pydantic import BaseModel, Field

from fdl.common import PATH_HIERARCHY, DimensionsFloat, DimensionsInt, PointFloat, find_by_attr
from fdl.rounding import RoundStrategy

if TYPE_CHECKING:
    from fdl.canvas import Canvas
    from fdl.context import Context
    from fdl.fdl import FDL
    from fdl.framingdecision import FramingDecision
    from fdl.framingintent import FramingIntent


# ---------------------------------------------------------------------------
# Geometry dataclass
# ---------------------------------------------------------------------------


@dataclass
class Geometry:
    """
    Geometry container for FDL template transformation processing.

    Holds all dimensions and anchor points as they progress through the
    normalize -> scale -> round -> clamp pipeline. Uses DimensionsFloat
    throughout for precision during calculations.

    Usage:
        source_geometry = Geometry(canvas_dims=..., effective_dims=..., ...)
        scaled_geometry = source_geometry.normalize_and_scale(...)
        rounded_geometry = scaled_geometry.round(...)
    """

    # Dimensions (all as DimensionsFloat for consistency)
    canvas_dims: DimensionsFloat
    effective_dims: DimensionsFloat
    protection_dims: DimensionsFloat
    framing_dims: DimensionsFloat

    # Anchor points
    effective_anchor: PointFloat
    protection_anchor: PointFloat
    framing_anchor: PointFloat

    def fill_hierarchy_gaps(self, anchor_offset: PointFloat) -> Geometry:
        """
        Fill gaps in the geometry hierarchy by propagating populated dimensions upward.

        The hierarchy from outermost to innermost is:
        - canvas.dimensions (outermost)
        - canvas.effective_dimensions
        - framing_decision.protection_dimensions
        - framing_decision.dimensions (innermost)

        The propagation logic:
        - If only framing is populated -> effective & canvas become framing
        - If protection is populated -> effective & canvas become protection
        - If effective is populated -> canvas becomes effective
        - If canvas is populated -> keep everything as is

        Special case: Protection dimensions are NEVER filled in from framing.
        If protection was not explicitly provided (is zero), it stays zero.
        This is because protection is an optional layer that must be explicitly defined.

        Anchors follow the same propagation logic as their corresponding dimensions.

        Returns
        -------
        Geometry
            New instance with gaps filled in the hierarchy.
        """
        # Start with current values
        canvas = self.canvas_dims
        effective = self.effective_dims
        protection = self.protection_dims
        framing = self.framing_dims

        effective_anchor = self.effective_anchor
        protection_anchor = self.protection_anchor
        framing_anchor = self.framing_anchor

        # Find the highest-ranking (outermost) non-zero dimension
        # and propagate it upward to fill gaps
        # Note: protection is special - it is NEVER filled from framing

        # Determine the reference dimension and anchor for propagation
        # We go from outermost to innermost to find the first populated layer
        if not canvas.is_zero():
            # Canvas is populated - use it to fill effective if needed
            reference_dims = canvas
            reference_anchor = PointFloat(x=0.0, y=0.0)  # Canvas has no anchor
        elif not effective.is_zero():
            # Effective is populated - use it to fill canvas
            reference_dims = effective
            reference_anchor = effective_anchor
        elif not protection.is_zero():
            # Protection is populated - use it to fill effective and canvas
            reference_dims = protection
            reference_anchor = protection_anchor
        else:
            # Only framing is populated - use it to fill effective and canvas
            # Note: We do NOT fill protection from framing (special case)
            reference_dims = framing
            reference_anchor = framing_anchor

        # Now propagate upward, filling any zero dimensions
        # Protection is special: NEVER fill it from framing
        # The check `protection.is_zero() and not reference_dims is protection`
        # ensures we only fill protection if reference came from a higher layer

        # Fill canvas if zero
        if canvas.is_zero():
            canvas = DimensionsFloat.from_dimensions(reference_dims)

        # Fill effective if zero (use the same reference)
        if effective.is_zero():
            effective = DimensionsFloat.from_dimensions(reference_dims)
            effective_anchor = PointFloat(x=reference_anchor.x, y=reference_anchor.y)

        # Protection is NEVER filled from framing - it stays zero if not provided
        # (no change to protection)

        effective_anchor -= anchor_offset
        protection_anchor -= anchor_offset
        framing_anchor -= anchor_offset

        return Geometry(
            canvas_dims=canvas,
            effective_dims=effective,
            protection_dims=protection,  # Unchanged - never propagated to
            framing_dims=framing,
            effective_anchor=effective_anchor.clamp(min_val=0.0),
            protection_anchor=protection_anchor.clamp(min_val=0.0),  # Unchanged order just offset - never propagated to
            framing_anchor=framing_anchor.clamp(min_val=0.0),
        )

    def get_dimensions_and_anchors_from_path(self, path: str) -> tuple[DimensionsFloat | DimensionsInt, PointFloat | None]:
        """
        Get dimensions and anchor from this Geometry object using a path string.

        Parameters
        ----------
        path : str
            The path to the dimensions (e.g., 'canvas.dimensions', 'framing_decision.dimensions').

        Returns
        -------
        Tuple[DimensionsFloat, PointFloat | None]
            The dimensions and anchor at the specified path.
        """
        if not path or path == "none":
            return DimensionsFloat(width=0.0, height=0.0), PointFloat(x=0.0, y=0.0)

        if path not in PATH_HIERARCHY:
            raise ValueError(f"Invalid path for FDL retrieval: {path}")

        if path == "canvas.dimensions":
            return self.canvas_dims, PointFloat(x=0.0, y=0.0)
        elif path == "canvas.effective_dimensions":
            return self.effective_dims, self.effective_anchor
        elif path == "framing_decision.protection_dimensions":
            return self.protection_dims, self.protection_anchor
        elif path == "framing_decision.dimensions":
            return self.framing_dims, self.framing_anchor
        else:
            raise ValueError(f"Invalid path for FDL retrieval: {path}")

    def normalize_and_scale(
        self,
        source_canvas_anamorphic_squeeze: float,
        scale_factor: float,
        target_anamorphic_squeeze: float,
    ) -> Geometry:
        """
        Create a new Geometry by normalizing and scaling all values.

        Applies normalize_and_scale to all dimensions and anchors, then
        calculates relative anchor positions by subtracting the anchor_offset.

        Parameters
        ----------

        source_canvas_anamorphic_squeeze : float
            Input anamorphic squeeze factor.
        scale_factor : float
            Scale factor to apply.
        target_anamorphic_squeeze : float
            Target anamorphic squeeze factor.

        Returns
        -------
        Geometry
            New instance with normalized, scaled, and relative values.
        """
        # Normalize and scale all dimensions
        canvas_scaled = self.canvas_dims.normalize_and_scale(source_canvas_anamorphic_squeeze, scale_factor, target_anamorphic_squeeze)
        effective_scaled = self.effective_dims.normalize_and_scale(
            source_canvas_anamorphic_squeeze, scale_factor, target_anamorphic_squeeze
        )
        protection_scaled = self.protection_dims.normalize_and_scale(
            source_canvas_anamorphic_squeeze, scale_factor, target_anamorphic_squeeze
        )
        framing_scaled = self.framing_dims.normalize_and_scale(source_canvas_anamorphic_squeeze, scale_factor, target_anamorphic_squeeze)

        # Normalize and scale all anchors, then make relative to anchor_offset
        effective_anchor = self.effective_anchor.normalize_and_scale(
            source_canvas_anamorphic_squeeze, scale_factor, target_anamorphic_squeeze
        )
        protection_anchor = self.protection_anchor.normalize_and_scale(
            source_canvas_anamorphic_squeeze, scale_factor, target_anamorphic_squeeze
        )
        framing_anchor = self.framing_anchor.normalize_and_scale(source_canvas_anamorphic_squeeze, scale_factor, target_anamorphic_squeeze)

        return Geometry(
            canvas_dims=canvas_scaled,
            effective_dims=effective_scaled,
            protection_dims=protection_scaled,
            framing_dims=framing_scaled,
            effective_anchor=effective_anchor,
            protection_anchor=protection_anchor,
            framing_anchor=framing_anchor,
        )

    def round(self, rounding: RoundStrategy) -> Geometry:
        """
        Round all dimensions and anchors according to template rounding rules.

        Parameters
        ----------
        rounding : RoundStrategy
            The rounding configuration (even/whole, up/down/round).

        Returns
        -------
        Geometry
            New instance with all values rounded.
        """
        return Geometry(
            canvas_dims=self.canvas_dims.round(rounding.even, rounding.mode),
            effective_dims=self.effective_dims.round(rounding.even, rounding.mode),
            protection_dims=self.protection_dims.round(rounding.even, rounding.mode),
            framing_dims=self.framing_dims.round(rounding.even, rounding.mode),
            effective_anchor=self.effective_anchor.round(rounding.even, rounding.mode),
            protection_anchor=self.protection_anchor.round(rounding.even, rounding.mode),
            framing_anchor=self.framing_anchor.round(rounding.even, rounding.mode),
        )

    def validate(self) -> None:
        """
        Validate geometry constraints.

        FDL Spec Reference: Section 7.4.5 - Geometry Validation

        Raises
        ------
        ValueError
            If framing dimensions are zero or effective dimensions are smaller
            than protection dimensions.
        """
        if self.framing_dims.is_zero():
            raise ValueError("Framing decision dimensions not provided")

        if not self.effective_dims.is_zero() and not self.protection_dims.is_zero():
            if self.effective_dims.width < self.protection_dims.width or self.effective_dims.height < self.protection_dims.height:
                raise ValueError("Source effective canvas dimensions are smaller than protection dimensions")

    def apply_offset(
        self,
        offset: PointFloat,
    ) -> tuple[Geometry, PointFloat, PointFloat, PointFloat]:
        """
        Apply offset to all anchors and return theoretical anchor positions.

        Theoretical anchors may be negative if content extends off-canvas.
        Anchors in the returned Geometry are clamped to >= 0; the theoretical
        anchors are returned separately for visible area calculation in Phase 9.

        FDL Spec Reference: Section 7.4.12 - Anchor Positioning

        Parameters
        ----------
        offset : PointFloat
            The content translation offset to apply to all anchors.

        Returns
        -------
        tuple[Geometry, PointFloat, PointFloat, PointFloat]
            (geometry with updated anchors, theoretical_effective_anchor,
             theoretical_protection_anchor, theoretical_framing_anchor)
        """
        # Calculate theoretical anchor positions (may be negative if content extends off-canvas)
        theoretical_effective_anchor = self.effective_anchor + offset
        theoretical_protection_anchor = self.protection_anchor + offset
        theoretical_framing_anchor = self.framing_anchor + offset

        return (
            Geometry(
                canvas_dims=self.canvas_dims,
                effective_dims=self.effective_dims,
                protection_dims=self.protection_dims,
                framing_dims=self.framing_dims,
                effective_anchor=theoretical_effective_anchor.clamp(min_val=0.0),
                protection_anchor=theoretical_protection_anchor.clamp(min_val=0.0),
                framing_anchor=theoretical_framing_anchor.clamp(min_val=0.0),
            ),
            theoretical_effective_anchor,
            theoretical_protection_anchor,
            theoretical_framing_anchor,
        )

    def crop(
        self,
        theoretical_effective_anchor: PointFloat,
        theoretical_protection_anchor: PointFloat,
        theoretical_framing_anchor: PointFloat,
    ) -> Geometry:
        """
        Crop all dimensions to visible portion within canvas, maintaining hierarchy.

        CROPPING IN FDL CONTEXT
        -----------------------
        When scaled content exceeds max_dims (overflow), we must "crop" - removing
        the invisible portions that extend beyond the output canvas boundaries.
        This is NOT destructive to the source; it calculates what portion of each
        layer is VISIBLE in the final output.

        Cropping uses "theoretical anchors" - anchor positions calculated as if there
        were no canvas boundary constraints. These can be NEGATIVE when content is
        shifted to align overflow:

        Example with RIGHT alignment and 400px X overflow:
            +----------------------------------+
            |         OUTPUT CANVAS            |
            |                                  |
        +---+----------------------------------+---+
        |   |   SCALED CONTENT                 |   |
        |   |   (protection layer)             |   |
        +---+----------------------------------+---+
            |                                  |
            +----------------------------------+
            ^                                  ^
        theoretical_anchor.x = -400      visible portion

        The theoretical anchor is -400 because content is shifted LEFT to align
        its right edge with the canvas right edge. The crop removes the 400px
        on the left that falls outside the visible canvas.

        LAYER HIERARCHY
        ---------------
        FDL defines nested layers that must maintain containment:
            canvas >= effective >= protection >= framing

        After individual cropping, we enforce this hierarchy to ensure inner
        layers never exceed their parent boundaries. This prevents artifacts
        where a child layer might appear to "poke through" its parent.

        FDL Spec Reference: Section 7.4.13 - Visible Area Calculation

        Parameters
        ----------
        theoretical_effective_anchor : PointFloat
            Unclamped effective anchor - may be negative if content shifted.
        theoretical_protection_anchor : PointFloat
            Unclamped protection anchor - may be negative if content shifted.
        theoretical_framing_anchor : PointFloat
            Unclamped framing anchor - may be negative if content shifted.

        Returns
        -------
        Geometry
            New geometry with all dimensions cropped to visible area within canvas.
        """

        def crop_dim(
            dims: DimensionsFloat,
            theo_anchor: PointFloat,
            clamped_anchor: PointFloat,
        ) -> DimensionsFloat:
            """Clip a dimension based on its theoretical anchor position."""
            if dims.is_zero():
                return dims

            # Calculate how much is clipped from left/top edge (negative anchor)
            clip_left = max(0.0, -theo_anchor.x)
            clip_top = max(0.0, -theo_anchor.y)
            # Reduce dimensions by clipped amount
            visible_w = dims.width - clip_left
            visible_h = dims.height - clip_top
            # Ensure doesn't extend beyond canvas right/bottom edge
            visible_w = min(visible_w, self.canvas_dims.width - clamped_anchor.x)
            visible_h = min(visible_h, self.canvas_dims.height - clamped_anchor.y)
            return DimensionsFloat(width=max(0.0, visible_w), height=max(0.0, visible_h))

        canvas_dims = self.canvas_dims
        # Clip all dimensions based on their theoretical anchors
        visible_effective = crop_dim(self.effective_dims, theoretical_effective_anchor, self.effective_anchor)
        visible_protection = crop_dim(self.protection_dims, theoretical_protection_anchor, self.protection_anchor)
        visible_framing = crop_dim(self.framing_dims, theoretical_framing_anchor, self.framing_anchor)

        # Enforce hierarchy: each layer <= parent
        # Canvas is already the bounds; effective must fit within canvas
        visible_effective, _ = visible_effective.clamp_to_dims(canvas_dims)
        # Protection must fit within effective (if protection exists)
        if not visible_protection.is_zero():
            visible_protection, _ = visible_protection.clamp_to_dims(visible_effective)
        # Framing must fit within protection (or effective if no protection)
        parent_dims = visible_protection if not visible_protection.is_zero() else visible_effective
        visible_framing, _ = visible_framing.clamp_to_dims(parent_dims)

        return Geometry(
            canvas_dims=canvas_dims,
            effective_dims=visible_effective,
            protection_dims=visible_protection,
            framing_dims=visible_framing,
            effective_anchor=self.effective_anchor,
            protection_anchor=self.protection_anchor,
            framing_anchor=self.framing_anchor,
        )


# ---------------------------------------------------------------------------
# TransformationResult dataclass
# ---------------------------------------------------------------------------


@dataclass
class TransformationResult:
    """Complete result from applying an FDL template transformation.

    Contains the output FDL with references to the created context, canvas,
    and framing decision, plus computed transformation values needed by
    downstream consumers (Nuke node graph, image processing).
    """

    fdl: FDL
    context_label: str
    canvas_id: str
    framing_decision_id: str
    scale_factor: float
    scaled_bounding_box: DimensionsFloat
    content_translation: PointFloat

    @property
    def context(self) -> Context:
        """Resolve the output context by label."""
        result = find_by_attr(self.fdl.contexts, "label", self.context_label)
        if result is None:
            raise ValueError(f"Context '{self.context_label}' not found in FDL")
        return result

    @property
    def canvas(self) -> Canvas:
        """Resolve the output canvas by ID."""
        for ctx in self.fdl.contexts:
            result = find_by_attr(ctx.canvases, "id", self.canvas_id)
            if result is not None:
                return result
        raise ValueError(f"Canvas '{self.canvas_id}' not found in FDL")

    @property
    def framing_decision(self) -> FramingDecision:
        """Resolve the output framing decision by ID."""
        canvas = self.canvas
        result = find_by_attr(canvas.framing_decisions, "id", self.framing_decision_id)
        if result is None:
            raise ValueError(f"FramingDecision '{self.framing_decision_id}' not found")
        return result


# ---------------------------------------------------------------------------
# Module-level public functions
# ---------------------------------------------------------------------------


def calculate_scale_factor(
    fit_norm: DimensionsFloat,
    target_norm: DimensionsFloat,
    fit_method: str,
) -> float:
    """
    Calculate scale factor based on fit_method.

    Per spec 7.4.7:
    - fit_all: min(width_ratio, height_ratio) - fits entirely within target
    - fill: max(width_ratio, height_ratio) - fills target completely (may crop)
    - width: width_ratio - fits width exactly
    - height: height_ratio - fits height exactly

    Parameters
    ----------
    fit_norm : DimensionsFloat
        Normalized fit source dimensions
    target_norm : DimensionsFloat
        Normalized target dimensions
    fit_method : str
        One of: "fit_all", "fill", "width", "height"

    Returns
    -------
    float
        Scale factor to apply
    """
    if fit_method == "fit_all":
        return min(target_norm.width / fit_norm.width, target_norm.height / fit_norm.height)
    elif fit_method == "fill":
        return max(target_norm.width / fit_norm.width, target_norm.height / fit_norm.height)
    elif fit_method == "width":
        return target_norm.width / fit_norm.width
    elif fit_method == "height":
        return target_norm.height / fit_norm.height
    else:
        raise ValueError(f"Unsupported fit_method: {fit_method}")


def get_dimensions_from_path(canvas: Canvas, framing: FramingDecision, path: str, required: bool = True) -> DimensionsFloat | None:
    """
    Get dimensions from a canvas or framing decision using a path string.

    Parameters
    ----------
    canvas : Canvas
        The canvas to extract dimensions from.
    framing : FramingDecision
        The framing decision to extract dimensions from.
    path : str
        The path to the dimensions (e.g., 'canvas.dimensions', 'framing_decision.dimensions').
    required : bool
        If True (default), raises ValueError when the path returns None.
        If False, returns None instead of raising an error for optional paths.
        Use required=True when validating explicit template paths (fit_source, preserve_from_source_canvas).
        Use required=False when auto-populating geometry from hierarchy.

    Returns
    -------
    DimensionsFloat or None
        The dimensions at the specified path, or None if not found and required=False.

    Raises
    ------
    ValueError
        If the path is not supported, not found, or (if required=True) the value is None.
    """
    if not path or path == "none":
        return DimensionsFloat(width=0.0, height=0.0)
    try:
        if path == "canvas.dimensions":
            return canvas.dimensions
        elif path == "canvas.effective_dimensions":
            dims = canvas.effective_dimensions
            if dims is None:
                if required:
                    raise ValueError(
                        f"Template references '{path}' but the source canvas does not have "
                        f"effective_dimensions defined. Either use a different fit_source/preserve_from_source_canvas "
                        f"in your template, or ensure the source FDL has effective_dimensions set."
                    )
                return None
            return dims
        elif path == "framing_decision.dimensions":
            return framing.dimensions
        elif path == "framing_decision.protection_dimensions":
            dims = framing.protection_dimensions
            if dims is None:
                if required:
                    raise ValueError(
                        f"Template references '{path}' but the source framing decision does not have "
                        f"protection_dimensions defined (framing_intent.protection is 0 or not set). "
                        f"Either use a different fit_source/preserve_from_source_canvas in your template "
                        f"(e.g., 'framing_decision.dimensions'), or ensure the source FDL has protection defined."
                    )
                return None
            return dims
    except KeyError:
        raise ValueError(f"Source path '{path}' not found in the provided FDL source.")
    raise ValueError(f"Unsupported source path: {path}")


def get_anchor_from_path(canvas: Canvas, framing: FramingDecision, path: str) -> PointFloat:
    """
    Get anchor point from a canvas or framing decision using a path string.

    Parameters
    ----------
    canvas : Canvas
        The canvas to extract anchor from.
    framing : FramingDecision
        The framing decision to extract anchor from.
    path : str
        The path to the anchor (e.g., 'canvas.dimensions', 'framing_decision.dimensions').

    Returns
    -------
    PointFloat
        The anchor point at the specified path.

    Raises
    ------
    ValueError
        If the path is not supported.
    """
    if not path or path == "none":
        return PointFloat(x=0.0, y=0.0)

    if path == "canvas.dimensions":
        return PointFloat(x=0.0, y=0.0)
    if path == "canvas.effective_dimensions":
        return canvas.effective_anchor_point or PointFloat(x=0.0, y=0.0)
    elif path == "framing_decision.dimensions":
        return framing.anchor_point
    elif path == "framing_decision.protection_dimensions":
        return framing.protection_anchor_point or PointFloat(x=0.0, y=0.0)

    raise ValueError(f"Unsupported source path for anchor point: {path}")


# ---------------------------------------------------------------------------
# Module-level private functions (pure math, no self needed)
# ---------------------------------------------------------------------------


def _alignment_factor(align: str) -> float:
    """
    Convert alignment string to numeric factor for unified alignment math.

    All alignment calculations reduce to: offset = (reference - content) * factor

    Parameters
    ----------
    align : str
        Alignment method: "left", "right", "top", "bottom", or "center".

    Returns
    -------
    float
        Factor: 0.0 (left/top), 0.5 (center), 1.0 (right/bottom).
    """
    align = (align or "center").lower()
    if align in ("left", "top"):
        return 0.0
    elif align in ("right", "bottom"):
        return 1.0
    return 0.5


def _output_size_for_axis(
    canvas_size: float,
    max_size: float,
    has_max: bool,
    pad_to_max: bool,
) -> float:
    """
    Determine output canvas size for a single axis.

    Each axis is evaluated independently:
    - PAD:  pad_to_maximum is set -> expand to max
    - CROP: canvas exceeds max   -> clamp to max
    - FIT:  no max constraint     -> use canvas as-is

    Returns
    -------
    float
        The output canvas size for this axis.
    """
    if has_max and pad_to_max:
        return float(max_size)
    if has_max and canvas_size > max_size:
        return float(max_size)
    return canvas_size


def _alignment_shift(
    fit_size: float,
    fit_anchor: float,
    output_size: float,
    canvas_size: float,
    target_size: float,
    is_center: bool,
    align_factor: float,
    pad_to_max: bool,
) -> float:
    """
    Calculate content translation shift for a single axis.

    Three regimes based on how the bounding box relates to the output:

    **FIT** (output == canvas, no pad_to_maximum):
        Content fills the output exactly. No shift.

    **PAD** (output > canvas, or pad_to_maximum is set):
        Position the fit within the output canvas.
        - CENTER, or fit >= target: center fit in output.
        - NON-CENTER with gap (fit < target): snap fit to target boundary.

    **CROP** (canvas > output, no pad_to_maximum):
        Bounding box exceeds the output -- decide what to show.
        - Fit already at origin and visible: no shift (clip edges only).
        - Fit itself overflows output: position fit using alignment factor.
        - Only bounding box overflows: shift by overflow x alignment factor.

    Parameters
    ----------
    fit_size : float
        Size of the fit_source layer on this axis.
    fit_anchor : float
        Offset of fit_source within the bounding box on this axis.
    output_size : float
        Final output canvas size on this axis.
    canvas_size : float
        Scaled bounding box size on this axis (before any crop/pad).
    target_size : float
        Target dimensions on this axis (virtual alignment reference).
    is_center : bool
        True if this axis uses center alignment.
    align_factor : float
        0.0 (left/top), 0.5 (center), 1.0 (right/bottom).
    pad_to_max : bool
        True if pad_to_maximum is set on the template.

    Returns
    -------
    float
        Content translation shift for this axis.
    """
    overflow = canvas_size - output_size

    # -- FIT ---------------------------------------------------------------
    # Output matches canvas exactly -- no space to align within.
    if abs(overflow) < 0.01 and not pad_to_max:
        return 0.0

    needs_crop = overflow > 0 and not pad_to_max

    if not needs_crop:
        # -- PAD (or pad_to_max with overflow) -----------------------------
        # Position the fit within the output canvas.
        gap = target_size - fit_size
        if not is_center and gap > 0:
            # Snap fit to target boundary (target starts at origin)
            return gap * align_factor - fit_anchor
        # Center fit in the output canvas
        return (output_size - fit_size) * 0.5 - fit_anchor

    # -- CROP --------------------------------------------------------------
    # Bounding box exceeds the output -- decide what to show.

    # If the fit is already at origin and fully visible, don't shift.
    # The overflow is only in the surrounding area; just clip the edges.
    if abs(fit_anchor) < 1.0 and fit_anchor + fit_size <= output_size:
        return 0.0

    # Fit itself overflows: position the fit within the output.
    if fit_size > output_size:
        return (output_size - fit_size) * align_factor - fit_anchor

    # Only the bounding box overflows: shift by the overflow amount.
    return -overflow * align_factor


# ---------------------------------------------------------------------------
# Literal type aliases
# ---------------------------------------------------------------------------

FitSource = Literal[
    "framing_decision.dimensions",
    "framing_decision.protection_dimensions",
    "canvas.dimensions",
    "canvas.effective_dimensions",
]
FitMethod = Literal["width", "height", "fit_all", "fill"]
AlignmentMethodVertical = Literal["top", "center", "bottom"]
AlignmentMethodHorizontal = Literal["left", "center", "right"]
PreserveFromSource = Literal[
    "none",
    "framing_decision.dimensions",
    "framing_decision.protection_dimensions",
    "canvas.dimensions",
    "canvas.effective_dimensions",
]


# ---------------------------------------------------------------------------
# CanvasTemplate model
# ---------------------------------------------------------------------------


class CanvasTemplate(BaseModel):
    label: Union[str, None] = None
    id: Annotated[str, Field(min_length=1, max_length=32)]
    target_dimensions: DimensionsInt
    target_anamorphic_squeeze: Annotated[float, Field(ge=0, default=1)]
    fit_source: Annotated[FitSource, Field(default="framing_decision.dimensions")]
    fit_method: Annotated[FitMethod, Field(default="width")]
    alignment_method_vertical: Annotated[
        AlignmentMethodVertical, Field(default="center")
    ]
    alignment_method_horizontal: Annotated[
        AlignmentMethodHorizontal, Field(default="center")
    ]
    preserve_from_source_canvas: Annotated[PreserveFromSource, Field(default="none")]
    maximum_dimensions: Annotated[
        Union[DimensionsInt, None], Field(default=None, exclude_if=lambda v: not v)
    ]
    pad_to_maximum: Annotated[
        bool, Field(default=False, exclude_if=lambda v: v is None)
    ]
    round: Annotated[RoundStrategy, Field(default=RoundStrategy(), exclude_if=lambda rnd: not rnd)]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def apply(
        self,
        source_canvas: Canvas,
        source_framing: FramingDecision,
        new_fd_name: str = "",
        source_context: Context | None = None,
        context_creator: str | None = None,
    ) -> TransformationResult:
        """
        Apply this canvas template following the Section 7.4 algorithm.

        The transformation pipeline:
        1. Populate source geometry from FDL paths
        2. Validate geometry constraints
        3. Fill hierarchy gaps and calculate anchor offsets
        4. Compute scale factor based on fit method
        5. Normalize, scale, and round geometry
        6. Apply maximum dimensions crop
        7. Calculate padding
        8. Calculate alignment and content translation
        9. Calculate visible framing dimensions
        10. Create output FDL objects

        Parameters
        ----------
        source_canvas : Canvas
            The source canvas to apply the template to.
        source_framing : FramingDecision
            The source framing decision.
        new_fd_name : str
            Name for the new framing decision.
        source_context : Context, optional
            The source context (used for label generation).
        context_creator : str, optional
            Creator name for the new context.

        Returns
        -------
        TransformationResult
            Complete result containing the output FDL, object IDs, and computed
            transformation values (scale_factor, scaled_bounding_box, content_translation).
        """
        # Derive template values inline (replaces TransformationConfig)
        input_squeeze = source_canvas.anamorphic_squeeze or 1.0
        target_squeeze = self.target_anamorphic_squeeze or 1.0
        if target_squeeze == 0.0:
            target_squeeze = input_squeeze
        fit_method = self.fit_method or "fit_all"
        preserve_path = self.preserve_from_source_canvas or ""
        max_dims = self.maximum_dimensions
        has_max_dims = max_dims is not None and not max_dims.is_zero()
        h_align = self.alignment_method_horizontal or "center"
        v_align = self.alignment_method_vertical or "center"
        target_dims_float = DimensionsFloat.from_dimensions(self.target_dimensions)

        # Phase 3: Populate and validate source geometry
        geometry = self._populate_source_geometry(source_canvas, source_framing, preserve_path)
        geometry.validate()

        # Phase 4: Prepare hierarchy and calculate anchor offset
        geometry, fit_dims = self._prepare_geometry_hierarchy(geometry, preserve_path)

        # Calculate the scale factor
        fit_dims_norm = fit_dims.normalize(input_squeeze)
        target_dims_norm = self.target_dimensions.normalize(target_squeeze)
        scale_factor = calculate_scale_factor(fit_dims_norm, target_dims_norm, fit_method)

        # Phase 5: Scale and round geometry
        geometry = geometry.normalize_and_scale(
            source_canvas_anamorphic_squeeze=input_squeeze,
            scale_factor=scale_factor,
            target_anamorphic_squeeze=target_squeeze,
        )
        geometry = geometry.round(self.round)

        # Extract scaled values BEFORE crop so they reflect the full scaled geometry
        scaled_fit, scaled_fit_anchor = geometry.get_dimensions_and_anchors_from_path(self.fit_source)
        scaled_bounding_box = geometry.canvas_dims

        # Phases 6-8: Calculate output canvas size and content translation (unified)
        output_canvas_dimensions, content_translation = self._calculate_output_canvas_and_translation(
            geometry, scaled_fit, scaled_fit_anchor,
            has_max_dims, max_dims, target_dims_float,
            h_align, v_align,
        )
        geometry.canvas_dims = output_canvas_dimensions

        # Phase 8b: Apply offsets to anchors - get ALL theoretical anchors
        geometry, theo_eff, theo_prot, theo_fram = geometry.apply_offset(content_translation)

        # Phase 9: Cropping ALL dimensions to visible canvas (uniform treatment)
        geometry = geometry.crop(theo_eff, theo_prot, theo_fram)

        # Phase 10: Create output FDL
        new_context, new_canvas, new_fd, new_fdl = self._create_output_fdl(
            geometry,
            target_squeeze,
            source_canvas,
            source_framing,
            new_fd_name,
            source_context,
            context_creator,
        )

        return TransformationResult(
            fdl=new_fdl,
            context_label=new_context.label,
            canvas_id=new_canvas.id,
            framing_decision_id=new_fd.id,
            scale_factor=scale_factor,
            scaled_bounding_box=scaled_bounding_box,
            content_translation=content_translation,
        )

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _populate_geometry_from_path(
        self,
        source_canvas: Canvas,
        source_framing: FramingDecision,
        start_path: str,
        geometry: dict,
    ) -> None:
        """
        Populate geometry dict from start_path and all paths below it in the hierarchy.

        The hierarchy is (from outermost to innermost):
        1. canvas.dimensions
        2. canvas.effective_dimensions
        3. framing_decision.protection_dimensions
        4. framing_decision.dimensions

        Starting from a path populates that level and all levels below it.
        """
        if start_path not in PATH_HIERARCHY:
            raise ValueError(f"Unknown path: {start_path}")

        start_index = PATH_HIERARCHY.index(start_path)

        for path in PATH_HIERARCHY[start_index:]:
            dimensions = get_dimensions_from_path(source_canvas, source_framing, path, required=False)
            anchor_point = get_anchor_from_path(source_canvas, source_framing, path)

            if path == "canvas.dimensions":
                if dimensions is not None:
                    geometry["canvas_dimensions"] = dimensions
            elif path == "canvas.effective_dimensions":
                if dimensions is not None:
                    geometry["canvas_effective_dimensions"] = dimensions
                    geometry["effective_anchor_point"] = anchor_point
            elif path == "framing_decision.protection_dimensions":
                if dimensions is not None:
                    geometry["framing_decision_protection_dimensions"] = dimensions
                    geometry["protection_anchor_point"] = anchor_point
            elif path == "framing_decision.dimensions":
                if dimensions is not None:
                    geometry["framing_decision_dimensions"] = dimensions
                    geometry["anchor_point"] = anchor_point

    def _populate_source_geometry(
        self,
        source_canvas: Canvas,
        source_framing: FramingDecision,
        preserve_path: str,
    ) -> Geometry:
        """
        Populate geometry from FDL paths based on template configuration.

        FDL Spec Reference: Section 7.4.4 - Source Geometry Population
        """
        geometry_dict: dict = {
            "canvas_dimensions": DimensionsInt(width=0, height=0),
            "canvas_effective_dimensions": DimensionsInt(width=0, height=0),
            "framing_decision_protection_dimensions": DimensionsFloat(width=0.0, height=0.0),
            "framing_decision_dimensions": DimensionsFloat(width=0.0, height=0.0),
            "effective_anchor_point": PointFloat(x=0.0, y=0.0),
            "protection_anchor_point": PointFloat(x=0.0, y=0.0),
            "anchor_point": PointFloat(x=0.0, y=0.0),
        }

        # Validate that explicitly requested template paths exist in the source
        if preserve_path and preserve_path != "none":
            if preserve_path not in PATH_HIERARCHY:
                raise ValueError("Unknown preserve_from_source_canvas")
            get_dimensions_from_path(source_canvas, source_framing, preserve_path, required=True)

        if self.fit_source not in PATH_HIERARCHY:
            raise ValueError("Unknown fit_source")
        get_dimensions_from_path(source_canvas, source_framing, self.fit_source, required=True)

        # Populate geometry from preserve_from_source_canvas (if specified)
        if preserve_path and preserve_path != "none":
            self._populate_geometry_from_path(source_canvas, source_framing, preserve_path, geometry_dict)

        # Populate geometry from fit_source (overwrites values from preserve_from_source_canvas if overlapping)
        self._populate_geometry_from_path(source_canvas, source_framing, self.fit_source, geometry_dict)

        return Geometry(
            canvas_dims=DimensionsFloat.from_dimensions(geometry_dict["canvas_dimensions"]),
            effective_dims=DimensionsFloat.from_dimensions(geometry_dict["canvas_effective_dimensions"]),
            protection_dims=geometry_dict["framing_decision_protection_dimensions"],
            framing_dims=geometry_dict["framing_decision_dimensions"],
            effective_anchor=geometry_dict["effective_anchor_point"],
            protection_anchor=geometry_dict["protection_anchor_point"],
            framing_anchor=geometry_dict["anchor_point"],
        )

    def _prepare_geometry_hierarchy(
        self,
        geometry: Geometry,
        preserve_path: str,
    ) -> tuple[Geometry, DimensionsFloat | DimensionsInt]:
        """
        Fill gaps in geometry hierarchy and calculate anchor offset.

        FDL Spec Reference: Section 7.4.6 - Hierarchy Gap Filling
        """
        fit_dims, fit_anchor = geometry.get_dimensions_and_anchors_from_path(self.fit_source)
        preserve_dims, preserve_anchor = geometry.get_dimensions_and_anchors_from_path(preserve_path)
        anchor_offset = fit_anchor if preserve_dims.is_zero() else preserve_anchor

        geometry = geometry.fill_hierarchy_gaps(anchor_offset)

        return geometry, fit_dims

    def _calculate_output_canvas_and_translation(
        self,
        geometry: Geometry,
        scaled_fit: DimensionsFloat,
        scaled_fit_anchor: PointFloat,
        has_max_dims: bool,
        max_dims: DimensionsInt | None,
        target_dims_float: DimensionsFloat,
        h_align: str,
        v_align: str,
    ) -> tuple[DimensionsFloat, PointFloat]:
        """
        Calculate output canvas dimensions and content translation.

        Evaluated independently per axis in two steps:

        1. **Output size** -- PAD (expand to max), CROP (clamp to max), or FIT (use canvas).
        2. **Alignment shift** -- position fit within output, or choose crop window.
        """
        canvas = geometry.canvas_dims

        # Step 1: output size per axis (independent)
        out_w = _output_size_for_axis(canvas.width, max_dims.width if has_max_dims else None, has_max_dims, self.pad_to_maximum)
        out_h = _output_size_for_axis(canvas.height, max_dims.height if has_max_dims else None, has_max_dims, self.pad_to_maximum)

        is_center_h = h_align == "center"
        is_center_v = v_align == "center"

        # Step 2: alignment shift per axis (independent)
        shift_x = _alignment_shift(
            scaled_fit.width,
            scaled_fit_anchor.x,
            out_w,
            canvas.width,
            target_dims_float.width,
            is_center_h,
            _alignment_factor(h_align),
            self.pad_to_maximum,
        )
        shift_y = _alignment_shift(
            scaled_fit.height,
            scaled_fit_anchor.y,
            out_h,
            canvas.height,
            target_dims_float.height,
            is_center_v,
            _alignment_factor(v_align),
            self.pad_to_maximum,
        )

        return DimensionsFloat(width=out_w, height=out_h), PointFloat(x=shift_x, y=shift_y)

    def _create_output_fdl(
        self,
        geometry: Geometry,
        target_anamorphic_squeeze: float,
        source_canvas: Canvas,
        source_framing: FramingDecision,
        new_fd_name: str,
        source_context: Context | None,
        context_creator: str | None,
    ) -> tuple[Context, Canvas, FramingDecision, FDL]:
        """
        Create output FDL objects from processed geometry.

        FDL Spec Reference: Section 7.4.14 - Output FDL Generation
        """
        from fdl.canvas import Canvas as CanvasModel
        from fdl.context import Context as ContextModel
        from fdl.fdl import FDL as FDLModel
        from fdl.framingdecision import FramingDecision as FramingDecisionModel
        from fdl.framingintent import FramingIntent as FramingIntentModel

        new_canvas_id = uuid.uuid4().hex[:30]

        # Generate labels
        default_label = self.label or "VFX Pull - Custom"
        if source_context:
            context_label = default_label
            canvas_label = f"{default_label}: {source_context.label} {source_canvas.label}"
        else:
            context_label = default_label
            canvas_label = default_label

        # Create new context
        new_context = ContextModel(label=context_label, context_creator=context_creator)

        # Create new canvas
        new_canvas = CanvasModel(
            id=new_canvas_id,
            label=canvas_label,
            dimensions=geometry.canvas_dims.to_int(),
            source_canvas_id=source_canvas.id,
            anamorphic_squeeze=target_anamorphic_squeeze,
            effective_dimensions=geometry.effective_dims.to_int(),
            effective_anchor_point=geometry.effective_anchor,
        )

        # Create new framing decision
        source_framing_intent_id = source_framing.framing_intent_id
        new_fd = FramingDecisionModel(
            id=f"{new_canvas_id}-{source_framing_intent_id}",
            framing_intent_id=source_framing_intent_id,
            dimensions=geometry.framing_dims,
            anchor_point=geometry.framing_anchor,
            protection_dimensions=geometry.protection_dims if not geometry.protection_dims.is_zero() else None,
            protection_anchor_point=geometry.protection_anchor if not geometry.protection_dims.is_zero() else None,
            label=new_fd_name,
        )
        new_canvas.framing_decisions.append(new_fd)
        new_context.canvases.append(source_canvas)
        new_context.canvases.append(new_canvas)

        # Create a default framing intent using the source's framing_intent_id
        default_framing_intent = FramingIntentModel(
            id=source_framing_intent_id,
            label="Default Framing Intent",
            aspect_ratio=DimensionsInt(width=1, height=1),
            protection=0.0,
        )
        new_fdl = FDLModel(
            default_framing_intent=default_framing_intent.id,
            framing_intents=[default_framing_intent],
            contexts=[new_context],
            canvas_templates=[self],
        )

        return new_context, new_canvas, new_fd, new_fdl

    # ------------------------------------------------------------------
    # Identity / hashing
    # ------------------------------------------------------------------

    def __eq__(self, other) -> bool:
        try:
            return self.id == other.id
        except AttributeError:
            return self.id == other

    def __hash__(self):
        return hash((self.id,))
