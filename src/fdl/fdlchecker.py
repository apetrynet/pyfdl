"""
FDL validation utilities for schema and structural validation.
"""

import json
import pathlib
from collections.abc import Callable
from typing import Any, ClassVar

import jsonschema


class FDLValidator:
    """
    Validator for FDL documents.

    Provides schema validation and structural validation rules including
    ID tree validation and dimension/anchor hierarchy validation.
    """

    SCHEMA_PATH = pathlib.Path(__file__).absolute().parent / "schema" / "v2.1" / "ascfdl.schema.json"

    # List of (name, validator_function) tuples to run in order
    # Each validator takes Dict[str, Any] and raises RuntimeError on failure
    _validators: ClassVar[list[tuple[str, Callable[[dict[str, Any]], None]]]] = []

    @classmethod
    def register_validator(cls, name: str, validator_fn: Callable[[dict[str, Any]], None]) -> None:
        """Register a validation function to be run during validate()."""
        cls._validators.append((name, validator_fn))

    @classmethod
    def validate(cls, fdl: dict[str, Any]) -> tuple[int, list[str]]:
        """
        Validate an FDL document against the JSON schema and all registered validators.

        Parameters
        ----------
        fdl : Dict[str, Any]
            The FDL document as a dictionary.

        Returns
        -------
        Tuple[int, List[str]]
            A tuple containing:
            - The number of validation errors found
            - A list of error message strings
        """
        errors = 0
        error_msgs = []

        # Schema validation
        with open(cls.SCHEMA_PATH) as f:
            schema = json.load(f)
            Validator = jsonschema.validators.validator_for(schema)
            v = Validator(schema=schema, format_checker=Validator.FORMAT_CHECKER)
            for error in v.iter_errors(fdl):
                error_msgs.append(str(error))
                errors += 1

        # Run all registered validators
        for name, validator_fn in cls._validators:
            try:
                validator_fn(fdl)
            except RuntimeError as e:
                error_msgs.append(f"{name} Error: {e}")
                errors += 1

        return errors, error_msgs

    @staticmethod
    def validate_id_tree(fdl: dict[str, Any]) -> None:
        """
        Validate the ID tree structure of an FDL document.

        Ensures all IDs are unique and properly referenced:
        - Framing intent IDs are unique
        - Canvas IDs are unique across all contexts
        - Framing decision IDs follow the format: {canvas_id}-{framing_intent_id}
        - All source_canvas_ids reference existing canvases
        - Canvas template IDs are unique

        Parameters
        ----------
        fdl : Dict[str, Any]
            The FDL document as a dictionary.

        Raises
        ------
        RuntimeError
            If any ID validation fails.
        """
        fi_ids = set()

        for fi in fdl.get("framing_intents", []):
            if "id" not in fi:
                raise RuntimeError("Framing Intent missing 'id'")
            fi_id = fi["id"]
            fi_label = fi.get("label", "(no label)")
            if fi_id in fi_ids:
                raise RuntimeError(f"Framing Intent {fi_id} ({fi_label}): ID duplicated")
            fi_ids.add(fi_id)

        if "default_framing_intent" in fdl and fdl["default_framing_intent"] is not None:
            default_framing_intent = fdl["default_framing_intent"]
            if default_framing_intent not in fi_ids:
                raise RuntimeError(f"Default Framing Intent {default_framing_intent}: Not in framing_intents")

        cv_ids = set()
        cv_source_canvas_ids = set()
        fd_ids = set()

        for cx in fdl.get("contexts", []):
            cx_label = cx.get("label", "(no label)")

            for cv in cx.get("canvases", []):
                cv_id = cv["id"]
                cv_label = cv.get("label", "(no label)")

                cv_source_canvas_id = cv["source_canvas_id"]
                cv_source_canvas_ids.add(cv_source_canvas_id)

                if cv_id in cv_ids:
                    raise RuntimeError(f"Context ({cx_label}) > Canvas {cv_id} ({cv_label}): ID duplicated")
                cv_ids.add(cv_id)

                for fd in cv.get("framing_decisions", []):
                    fd_id = fd["id"]

                    if fd_id in fd_ids:
                        raise RuntimeError(f"Context ({cx_label}) > Canvas {cv_id} ({cv_label}) > Framing Decision {fd_id}: ID duplicated")
                    fd_ids.add(fd_id)

                    fd_framing_intent_id = fd["framing_intent_id"]

                    if fd_framing_intent_id not in fi_ids:
                        raise RuntimeError(
                            f"Context ({cx_label}) > Canvas {cv_id} ({cv_label}) > Framing Decision {fd_id}: "
                            f"Framing Intent ID {fd_framing_intent_id} not in framing_intents"
                        )

                    expected_fd_id = f"{cv_id}-{fd_framing_intent_id}"
                    if fd_id != expected_fd_id:
                        raise RuntimeError(
                            f"Context ({cx_label}) > Canvas {cv_id} ({cv_label}) > Framing Decision {fd_id}: "
                            f"ID doesn't match expected {expected_fd_id}"
                        )

        unrecognised_cv_ids = cv_source_canvas_ids - cv_ids
        if len(unrecognised_cv_ids) > 0:
            raise RuntimeError(f"Source Canvas IDs {list(unrecognised_cv_ids)} not in canvases")

        ct_ids = set()
        for ct in fdl.get("canvas_templates", []):
            ct_id = ct["id"]
            ct_label = ct["label"]

            if ct_id in ct_ids:
                raise RuntimeError(f"Canvas Template {ct_id} ({ct_label}): ID duplicated")
            ct_ids.add(ct_id)

    # Path hierarchy from outermost to innermost (matches utils._PATH_HIERARCHY)
    _PATH_HIERARCHY: ClassVar[list[str]] = [
        "canvas.dimensions",
        "canvas.effective_dimensions",
        "framing_decision.protection_dimensions",
        "framing_decision.dimensions",
    ]

    @staticmethod
    def _get_dims_and_anchor_from_path(path: str, canvas: dict[str, Any], fd: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Extract dimensions and anchor for a given path from raw FDL dicts.

        Returns (None, None) if the path's data doesn't exist (optional fields).
        """
        if path == "canvas.dimensions":
            dims = canvas.get("dimensions")
            anchor = {"x": 0, "y": 0}  # Canvas always at origin
            return dims, anchor
        elif path == "canvas.effective_dimensions":
            dims = canvas.get("effective_dimensions")
            if dims is None:
                return None, None
            anchor = canvas.get("effective_anchor_point", {"x": 0, "y": 0})
            return dims, anchor
        elif path == "framing_decision.protection_dimensions":
            dims = fd.get("protection_dimensions")
            if dims is None:
                return None, None
            anchor = fd.get("protection_anchor_point", {"x": 0, "y": 0})
            return dims, anchor
        elif path == "framing_decision.dimensions":
            dims = fd.get("dimensions")
            anchor = fd.get("anchor_point", {"x": 0, "y": 0})
            return dims, anchor
        return None, None

    @classmethod
    def validate_dimension_hierarchy(cls, fdl_dict: dict[str, Any]) -> None:
        """
        Validate the dimension and anchor hierarchy of an FDL document.

        Traverses the path hierarchy (outer to inner):
            Canvas -> Effective (optional) -> Protection (optional) -> Framing

        Validates for each pair of PRESENT levels:
        - Dimensions: outer >= inner (width and height)
        - Anchors: outer <= inner (x and y grow as you go inward)

        Optional fields (effective_dimensions, protection_dimensions) are skipped
        if not present in the FDL.

        Parameters
        ----------
        fdl_dict : Dict[str, Any]
            The FDL document as a dictionary.

        Raises
        ------
        RuntimeError
            If any dimension or anchor hierarchy validation fails.
        """
        for ctx in fdl_dict.get("contexts", []):
            ctx_label = ctx.get("label", "(no label)")

            for canvas in ctx.get("canvases", []):
                cv_id = canvas.get("id", "(no id)")
                cv_label = canvas.get("label", "(no label)")
                location = f"Context ({ctx_label}) > Canvas {cv_id} ({cv_label})"

                for fd in canvas.get("framing_decisions", []):
                    fd_id = fd.get("id", "(no id)")
                    fd_location = f"{location} > FD {fd_id}"

                    # Collect only PRESENT levels in hierarchy (skip optional missing fields)
                    levels = []
                    for path in cls._PATH_HIERARCHY:
                        dims, anchor = cls._get_dims_and_anchor_from_path(path, canvas, fd)
                        if dims is not None:
                            levels.append(
                                {
                                    "path": path,
                                    "dims": dims,
                                    "anchor": anchor,
                                }
                            )

                    # Validate adjacent pairs of present levels (outer to inner)
                    for i in range(len(levels) - 1):
                        outer = levels[i]
                        inner = levels[i + 1]

                        outer_w = outer["dims"].get("width", 0)
                        outer_h = outer["dims"].get("height", 0)
                        inner_w = inner["dims"].get("width", 0)
                        inner_h = inner["dims"].get("height", 0)

                        outer_x = outer["anchor"].get("x", 0)
                        outer_y = outer["anchor"].get("y", 0)
                        inner_x = inner["anchor"].get("x", 0)
                        inner_y = inner["anchor"].get("y", 0)

                        outer_name = outer["path"].replace("_", " ").replace(".", " ")
                        inner_name = inner["path"].replace("_", " ").replace(".", " ")

                        # Dimensions: outer >= inner
                        if inner_w > outer_w or inner_h > outer_h:
                            raise RuntimeError(
                                f"{fd_location}: {inner_name} ({inner_w}x{inner_h}) exceeds "
                                f"{outer_name} ({outer_w}x{outer_h}). "
                                f"Required hierarchy: {outer_name} >= {inner_name}"
                            )

                        # Anchors: outer <= inner (anchors grow inward)
                        if inner_x < outer_x or inner_y < outer_y:
                            raise RuntimeError(
                                f"{fd_location}: {inner_name} anchor ({inner_x}, {inner_y}) is outside "
                                f"{outer_name} anchor ({outer_x}, {outer_y}). "
                                f"Required hierarchy: {outer_name} anchor <= {inner_name} anchor"
                            )

    @staticmethod
    def validate_non_negative_anchors(fdl_dict: dict[str, Any]) -> None:
        """
        Validate that all anchor points have non-negative x and y values.

        Parameters
        ----------
        fdl_dict : Dict[str, Any]
            The FDL document as a dictionary.

        Raises
        ------
        RuntimeError
            If any anchor point has negative x or y values.
        """
        for ctx in fdl_dict.get("contexts", []):
            ctx_label = ctx.get("label", "(no label)")

            for canvas in ctx.get("canvases", []):
                cv_id = canvas.get("id", "(no id)")
                cv_label = canvas.get("label", "(no label)")
                location = f"Context ({ctx_label}) > Canvas {cv_id} ({cv_label})"

                # Check effective_anchor_point
                eff_anchor = canvas.get("effective_anchor_point")
                if eff_anchor:
                    x, y = eff_anchor.get("x", 0), eff_anchor.get("y", 0)
                    if x < 0 or y < 0:
                        raise RuntimeError(
                            f"{location}: effective_anchor_point ({x}, {y}) has negative values. Anchor coordinates must be >= 0."
                        )

                for fd in canvas.get("framing_decisions", []):
                    fd_id = fd.get("id", "(no id)")
                    fd_location = f"{location} > FD {fd_id}"

                    # Check anchor_point (framing)
                    anchor = fd.get("anchor_point")
                    if anchor:
                        x, y = anchor.get("x", 0), anchor.get("y", 0)
                        if x < 0 or y < 0:
                            raise RuntimeError(
                                f"{fd_location}: anchor_point ({x}, {y}) has negative values. Anchor coordinates must be >= 0."
                            )

                    # Check protection_anchor_point
                    prot_anchor = fd.get("protection_anchor_point")
                    if prot_anchor:
                        x, y = prot_anchor.get("x", 0), prot_anchor.get("y", 0)
                        if x < 0 or y < 0:
                            raise RuntimeError(
                                f"{fd_location}: protection_anchor_point ({x}, {y}) has negative values. Anchor coordinates must be >= 0."
                            )

    @staticmethod
    def validate_anchors_within_canvas(fdl_dict: dict[str, Any]) -> None:
        """
        Validate that all anchor points are within the canvas dimensions.

        Parameters
        ----------
        fdl_dict : Dict[str, Any]
            The FDL document as a dictionary.

        Raises
        ------
        RuntimeError
            If any anchor point exceeds the canvas dimensions.
        """
        for ctx in fdl_dict.get("contexts", []):
            ctx_label = ctx.get("label", "(no label)")

            for canvas in ctx.get("canvases", []):
                cv_id = canvas.get("id", "(no id)")
                cv_label = canvas.get("label", "(no label)")
                location = f"Context ({ctx_label}) > Canvas {cv_id} ({cv_label})"

                # Get canvas dimensions (always present)
                canvas_dims = canvas.get("dimensions", {})
                canvas_width = canvas_dims.get("width", 0)
                canvas_height = canvas_dims.get("height", 0)

                # Check effective_anchor_point
                eff_anchor = canvas.get("effective_anchor_point")
                if eff_anchor:
                    x, y = eff_anchor.get("x", 0), eff_anchor.get("y", 0)
                    if x > canvas_width or y > canvas_height:
                        raise RuntimeError(
                            f"{location}: effective_anchor_point ({x}, {y}) exceeds "
                            f"canvas dimensions ({canvas_width}x{canvas_height}). "
                            f"Anchor coordinates must be within canvas bounds."
                        )

                for fd in canvas.get("framing_decisions", []):
                    fd_id = fd.get("id", "(no id)")
                    fd_location = f"{location} > FD {fd_id}"

                    # Check anchor_point (framing)
                    anchor = fd.get("anchor_point")
                    if anchor:
                        x, y = anchor.get("x", 0), anchor.get("y", 0)
                        if x > canvas_width or y > canvas_height:
                            raise RuntimeError(
                                f"{fd_location}: anchor_point ({x}, {y}) exceeds "
                                f"canvas dimensions ({canvas_width}x{canvas_height}). "
                                f"Anchor coordinates must be within canvas bounds."
                            )

                    # Check protection_anchor_point
                    prot_anchor = fd.get("protection_anchor_point")
                    if prot_anchor:
                        x, y = prot_anchor.get("x", 0), prot_anchor.get("y", 0)
                        if x > canvas_width or y > canvas_height:
                            raise RuntimeError(
                                f"{fd_location}: protection_anchor_point ({x}, {y}) exceeds "
                                f"canvas dimensions ({canvas_width}x{canvas_height}). "
                                f"Anchor coordinates must be within canvas bounds."
                            )


# Register default validators
FDLValidator.register_validator("ID Tree", FDLValidator.validate_id_tree)
FDLValidator.register_validator("Dimension Hierarchy", FDLValidator.validate_dimension_hierarchy)
FDLValidator.register_validator("Non-Negative Anchors", FDLValidator.validate_non_negative_anchors)
FDLValidator.register_validator("Anchors Within Canvas", FDLValidator.validate_anchors_within_canvas)


# Backward-compatible module-level function
def validate_fdl(fdl: dict[str, Any]) -> tuple[int, list[str]]:
    """
    Validate an FDL document against the JSON schema and validation rules.

    This is a convenience wrapper around FDLValidator.validate().

    Parameters
    ----------
    fdl : Dict[str, Any]
        The FDL document as a dictionary.

    Returns
    -------
    Tuple[int, List[str]]
        A tuple containing:
        - The number of validation errors found
        - A list of error message strings
    """
    return FDLValidator.validate(fdl)
