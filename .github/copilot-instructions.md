# Copilot Instructions for FastKML

## 1. Overview
This file provides instructions for AI coding assistants (like GitHub Copilot) to generate code that aligns with the `fastkml` project's architecture, style, and conventions. It is based on observed patterns in the codebase.

## 2. File Category Reference

### Source Code (`fastkml/**/*.py`)
- **Description**: Core library logic.
- **Conventions**:
    - **Type Hints**: Mandatory and strict (`mypy`). Use `typing_extensions.Self` for fluent interfaces.
    - **Formatting**: `black` style (88 chars).
    - **Linting**: `ruff` rules must be followed.
    - **Docstrings**: NumPy/SciPy style.
    - **Inheritance**: All KML objects must inherit from `fastkml.base._XMLObject`.

### Tests (`tests/**/*.py`)
- **Description**: Unit and property-based tests.
- **Conventions**:
    - **Framework**: `pytest`.
    - **Property Testing**: `hypothesis` is heavily used for generating test data.
    - **Naming**: `*_test.py`.

### Examples (`examples/**/*.py`)
- **Description**: Usage demonstrations.
- **Conventions**: Simple, runnable scripts.

## 3. Feature Scaffold Guide

To implement a new KML feature (e.g., a new KML element):

1.  **Identify the Domain**: Is it a Feature, Container, Geometry, or Extension?
2.  **Create/Modify Class**:
    - Place in `fastkml/features.py`, `fastkml/geometry.py`, etc.
    - Inherit from `_XMLObject` (or `_BaseObject`, `_Geometry`).
    - Implement `__init__` accepting `ns`, `name_spaces`, and `**kwargs`.
    - Implement `get_tag_name`.
3.  **Register the Class**:
    - **CRITICAL**: Add a `registry.register()` call in `fastkml/registry.py` (or the module itself).
    - Define a `RegistryItem` mapping attributes to XML nodes/attributes.
4.  **Add Tests**:
    - Create a test file in `tests/` (e.g., `tests/new_feature_test.py`).
    - Add `hypothesis` strategies if applicable.

## 4. Integration Rules

### Registry System
- **Constraint**: Do NOT manually parse or write XML attributes in `to_string` or `from_string`.
- **Requirement**: Use the global `registry` to define how Python attributes map to XML.

### XML Handling
- **Constraint**: Do NOT import `lxml` or `xml.etree` directly.
- **Requirement**: Use `fastkml.config.etree` to ensure compatibility.

### Geometry
- **Constraint**: Geometry classes must be mutually exclusive regarding raw geometry vs. KML coordinates in `__init__`.
- **Requirement**: Implement `__geo_interface__` compatibility where possible.

## 5. Example Prompt Usage

**User Prompt:**
> "Add support for the KML 'Camera' element."

**Copilot Response:**
1.  **`fastkml/views.py`** (or similar):
    ```python
    class Camera(_XMLObject):
        """KML Camera element."""

        # ... attributes like longitude, latitude, altitude, heading, tilt, roll ...

        def __init__(self, ns=None, name_spaces=None, **kwargs):
            super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
            # ... initialization ...

        @classmethod
        def get_tag_name(cls):
            return "Camera"
    ```
2.  **`fastkml/registry.py`**:
    ```python
    registry.register(
        Camera,
        RegistryItem(
            ns_ids=("kml", "gx"),
            classes=(float,),
            attr_name="longitude",
            node_name="longitude",
            get_kwarg=xml_subelement_kwarg,
            set_element=xml_subelement,
        ),
        # ... other attributes ...
    )
    ```
3.  **`tests/camera_test.py`**:
    ```python
    def test_camera_serialization():
        cam = Camera(longitude=10.0, latitude=20.0)
        assert "<longitude>10.0</longitude>" in cam.to_string()
    ```
