---
title: "Network Updates And Atom"
description: "Reference for network-link update actions, NetworkLinkControl, and Atom metadata objects."
---

Import paths:

```python
from fastkml import Change, Create, Delete, NetworkLinkControl, Update
from fastkml import AtomAuthor, AtomContributor, AtomLink
```

Source files:

- `fastkml/network_link_control.py`
- `fastkml/atom.py`

## Update action classes

```python
Create(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, objects: Optional[Iterable[_XMLObject]] = None, **kwargs: Any) -> None
Delete(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, objects: Optional[Iterable[_XMLObject]] = None, **kwargs: Any) -> None
Change(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, objects: Optional[Iterable[_XMLObject]] = None, **kwargs: Any) -> None
Update(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, target_href: Optional[str] = None, operations: Optional[Iterable[Union[Create, Delete, Change]]] = None, **kwargs: Any) -> None
NetworkLinkControl(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, min_refresh_period: Optional[float] = None, max_session_length: Optional[float] = None, cookie: Optional[str] = None, message: Optional[str] = None, link_name: Optional[str] = None, link_description: Optional[str] = None, link_snippet: Optional[str] = None, expires: Optional[KmlDateTime] = None, view: Optional[Union[Camera, LookAt]] = None, update: Optional[Update] = None, **kwargs: Any) -> None
```

Use these classes when you are producing KML meant to update data already loaded through a network link.

## Atom metadata classes

```python
AtomLink(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, href: Optional[str] = None, rel: Optional[str] = None, type: Optional[str] = None, hreflang: Optional[str] = None, title: Optional[str] = None, length: Optional[int] = None, **kwargs: Any) -> None
AtomAuthor(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, name: Optional[str] = None, uri: Optional[str] = None, email: Optional[str] = None, **kwargs: Any) -> None
AtomContributor(ns: Optional[str] = None, name_spaces: Optional[dict[str, str]] = None, name: Optional[str] = None, uri: Optional[str] = None, email: Optional[str] = None, **kwargs: Any) -> None
```

These objects attach to `_Feature.atom_link` and `_Feature.atom_author` and are useful when you want author or related-link metadata embedded directly in the KML.

Example:

```python
from fastkml import Change, NetworkLinkControl, Placemark, Update

change = Change(objects=[Placemark(target_id="pm-123" name="Updated name")])
update = Update(target_href="https://example.com/original.kml" operations=[change])
control = NetworkLinkControl(message="Applying remote update" update=update)

print(bool(control.update))
```

The registry setup in `fastkml/_registry_setup.py` matters here because it fills in which classes `Create`, `Delete`, and `Change` are allowed to contain. Without those registrations, the update action payloads would not deserialize correctly.
