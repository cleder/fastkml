"""Overlays."""

import logging
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Union
from typing import cast

from fastkml import atom
from fastkml import config
from fastkml import gx
from fastkml.base import _XMLObject
from fastkml.data import ExtendedData
from fastkml.enums import AltitudeMode
from fastkml.enums import GridOrigin
from fastkml.enums import Shape
from fastkml.enums import Verbosity
from fastkml.features import Snippet
from fastkml.features import _Feature
from fastkml.geometry import LinearRing
from fastkml.geometry import LineString
from fastkml.geometry import MultiGeometry
from fastkml.geometry import Point
from fastkml.geometry import Polygon
from fastkml.links import Icon
from fastkml.styles import Style
from fastkml.styles import StyleMap
from fastkml.styles import StyleUrl
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp
from fastkml.types import Element
from fastkml.views import Camera
from fastkml.views import LookAt
from fastkml.views import Region

logger = logging.getLogger(__name__)

KmlGeometry = Union[
    Point,
    LineString,
    LinearRing,
    Polygon,
    MultiGeometry,
    gx.MultiTrack,
    gx.Track,
]


class _Overlay(_Feature):
    """
    abstract element; do not create.

    Base type for image overlays drawn on the planet surface or on the screen

    A Container element holds one or more Features and allows the creation of
    nested hierarchies.
    """

    _color: Optional[str]
    # Color values expressed in hexadecimal notation, including opacity (alpha)
    # values. The order of expression is alphaOverlay, blue, green, red
    # (AABBGGRR). The range of values for any one color is 0 to 255 (00 to ff).
    # For opacity, 00 is fully transparent and ff is fully opaque.

    _draw_order: Optional[int]
    # Defines the stacking order for the images in overlapping overlays.
    # Overlays with higher <drawOrder> values are drawn on top of those with
    # lower <drawOrder> values.

    _icon: Optional[Icon]
    # Defines the image associated with the overlay. Contains an <href> html
    # tag which defines the location of the image to be used as the overlay.
    # The location can be either on a local file system or on a webserver. If
    # this element is omitted or contains no <href>, a rectangle is drawn using
    # the color and size defined by the ground or screen overlay.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        visibility: Optional[bool] = None,
        isopen: Optional[bool] = None,
        atom_link: Optional[atom.Link] = None,
        atom_author: Optional[atom.Author] = None,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
        snippet: Optional[Snippet] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[StyleUrl] = None,
        styles: Optional[Iterable[Union[Style, StyleMap]]] = None,
        region: Optional[Region] = None,
        extended_data: Optional[ExtendedData] = None,
        # Overlay specific
        color: Optional[str] = None,
        draw_order: Optional[int] = None,
        icon: Optional[Icon] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            name=name,
            visibility=visibility,
            isopen=isopen,
            atom_link=atom_link,
            atom_author=atom_author,
            address=address,
            phone_number=phone_number,
            snippet=snippet,
            description=description,
            view=view,
            times=times,
            style_url=style_url,
            styles=styles,
            region=region,
            extended_data=extended_data,
        )
        self._icon = icon
        self._color = color
        self._draw_order = draw_order

    @property
    def color(self) -> Optional[str]:
        return self._color

    @color.setter
    def color(self, color: Optional[str]) -> None:
        self._color = color

    @property
    def draw_order(self) -> Optional[int]:
        return self._draw_order

    @draw_order.setter
    def draw_order(self, value: Optional[int]) -> None:
        self._draw_order = value

    @property
    def icon(self) -> Optional[Icon]:
        return self._icon

    @icon.setter
    def icon(self, value: Optional[Icon]) -> None:
        self._icon = value

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self._color:
            color = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}color",
            )
            color.text = self._color
        if self._draw_order:
            draw_order = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}drawOrder",
            )
            draw_order.text = str(self._draw_order)
        if self._icon:
            element.append(self._icon.etree_element())
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        color = element.find(f"{ns}color")
        if color is not None:
            kwargs["color"] = color.text
        draw_order = element.find(f"{ns}drawOrder")
        if draw_order is not None:
            kwargs["draw_order"] = int(draw_order.text)
        icon = element.find(f"{ns}Icon")
        if icon is not None:
            kwargs["icon"] = cast(
                Icon,
                Icon.class_from_element(
                    ns=ns,
                    name_spaces=name_spaces,
                    element=icon,
                    strict=strict,
                ),
            )
        return kwargs


class ViewVolume(_XMLObject):
    """
    The ViewVolume defines how much of the current scene is visible.

    Specifying the field of view is analogous to specifying the lens opening in a
    physical camera.
    A small field of view, like a telephoto lens, focuses on a small part of the scene.
    A large field of view, like a wide-angle lens, focuses on a large part of the scene.

    https://developers.google.com/kml/documentation/kmlreference#viewvolume
    """

    left_fow: Optional[float]
    # Angle, in degrees, between the camera's viewing direction and the left side
    # of the view volume.

    right_fov: Optional[float]
    # Angle, in degrees, between the camera's viewing direction and the right side
    # of the view volume.

    bottom_fov: Optional[float]
    # Angle, in degrees, between the camera's viewing direction and the bottom side
    # of the view volume.

    top_fov: Optional[float]
    # Angle, in degrees, between the camera's viewing direction and the top side
    # of the view volume.

    near: Optional[float]
    # Measurement in meters along the viewing direction from the camera viewpoint
    # to the PhotoOverlay shape.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        left_fov: Optional[float] = None,
        right_fov: Optional[float] = None,
        bottom_fov: Optional[float] = None,
        top_fov: Optional[float] = None,
        near: Optional[float] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.left_fov = left_fov
        self.right_fov = right_fov
        self.bottom_fov = bottom_fov
        self.top_fov = top_fov
        self.near = near

    def __bool__(self) -> bool:
        return all(
            [
                self.left_fov is not None,
                self.right_fov is not None,
                self.bottom_fov is not None,
                self.top_fov is not None,
                self.near is not None,
            ],
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        left_fov = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}leftFov",
        )
        left_fov.text = str(self.left_fov)
        right_fov = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}rightFov",
        )
        right_fov.text = str(self.right_fov)
        bottom_fov = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}bottomFov",
        )
        bottom_fov.text = str(self.bottom_fov)
        top_fov = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}topFov",
        )
        top_fov.text = str(self.top_fov)
        near = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}near",
        )
        near.text = str(self.near)
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        left_fov = element.find(f"{ns}leftFov")
        if left_fov is not None:
            kwargs["left_fov"] = float(left_fov.text)
        right_fov = element.find(f"{ns}rightFov")
        if right_fov is not None:
            kwargs["right_fov"] = float(right_fov.text)
        bottom_fov = element.find(f"{ns}bottomFov")
        if bottom_fov is not None:
            kwargs["bottom_fov"] = float(bottom_fov.text)
        top_fov = element.find(f"{ns}topFov")
        if top_fov is not None:
            kwargs["top_fov"] = float(top_fov.text)
        near = element.find(f"{ns}near")
        if near is not None:
            kwargs["near"] = float(near.text)
        return kwargs


class ImagePyramid(_XMLObject):
    """
    For very large images, you'll need to construct an image pyramid.

    An ImagePyramid is a hierarchical set of images, each of which is an increasingly
    lower resolution version of the original image.
    Each image in the pyramid is subdivided into tiles, so that only the portions in
    view need to be loaded.
    Google Earth calculates the current viewpoint and loads the tiles that are
    appropriate to the user's distance from the image.
    As the viewpoint moves closer to the PhotoOverlay, Google Earth loads higher
    resolution tiles.
    Since all the pixels in the original image can't be viewed on the screen at once,
    this preprocessing allows Google Earth to achieve maximum performance because it
    loads only the portions of the image that are in view, and only the pixel details
    that can be discerned by the user at the current viewpoint.

    When you specify an image pyramid, you also need to modify the <href> in the <Icon>
    element to include specifications for which tiles to load.
    """

    tile_size: Optional[int]
    # Size of the tiles, in pixels. Tiles must be square, and <tileSize> must be a power
    # of 2. A tile size of 256 (the default) or 512 is recommended.
    # The original image is divided into tiles of this size, at varying resolutions.

    max_width: Optional[int]
    # Width in pixels of the original image.

    max_height: Optional[int]
    # Height in pixels of the original image.

    grid_origin: Optional[GridOrigin]
    # Specifies where to begin numbering the tiles in each layer of the pyramid.
    # A value of lowerLeft specifies that row 1, column 1 of each layer is in
    # the bottom left corner of the grid.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        tile_size: Optional[int] = None,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        grid_origin: Optional[GridOrigin] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.tile_size = tile_size
        self.max_width = max_width
        self.max_height = max_height
        self.grid_origin = grid_origin

    def __bool__(self) -> bool:
        return (
            self.tile_size is not None
            and self.max_width is not None
            and self.max_height is not None
            and self.grid_origin is not None
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        tile_size = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}tileSize",
        )
        tile_size.text = str(self.tile_size)
        max_width = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}maxWidth",
        )
        max_width.text = str(self.max_width)
        max_height = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}maxHeight",
        )
        max_height.text = str(self.max_height)
        grid_origin = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}gridOrigin",
        )
        assert self.grid_origin is not None
        grid_origin.text = self.grid_origin.value
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        tile_size = element.find(f"{ns}tileSize")
        if tile_size is not None:
            kwargs["tile_size"] = int(tile_size.text)
        max_width = element.find(f"{ns}maxWidth")
        if max_width is not None:
            kwargs["max_width"] = int(max_width.text)
        max_height = element.find(f"{ns}maxHeight")
        if max_height is not None:
            kwargs["max_height"] = int(max_height.text)
        grid_origin = element.find(f"{ns}gridOrigin")
        if grid_origin is not None:
            kwargs["grid_origin"] = GridOrigin(grid_origin.text)
        return kwargs


class PhotoOverlay(_Overlay):
    """
    The <PhotoOverlay> element allows you to geographically locate a photograph
    on the Earth and to specify viewing parameters for this PhotoOverlay.
    The PhotoOverlay can be a simple 2D rectangle, a partial or full cylinder,
    or a sphere (for spherical panoramas). The overlay is placed at the
    specified location and oriented toward the viewpoint.

    Because <PhotoOverlay> is derived from <Feature>, it can contain one of
    the two elements derived from <AbstractView>—either <Camera> or <LookAt>.
    The Camera (or LookAt) specifies a viewpoint and a viewing direction (also
    referred to as a view vector). The PhotoOverlay is positioned in relation
    to the viewpoint. Specifically, the plane of a 2D rectangular image is
    orthogonal (at right angles to) the view vector. The normal of this
    plane—that is, its front, which is the part
    with the photo—is oriented toward the viewpoint.

    The URL for the PhotoOverlay image is specified in the <Icon> tag,
    which is inherited from <Overlay>. The <Icon> tag must contain an <href>
    element that specifies the image file to use for the PhotoOverlay.
    In the case of a very large image, the <href> is a special URL that
    indexes into a pyramid of images of varying resolutions (see ImagePyramid).

    https://developers.google.com/kml/documentation/kmlreference#photooverlay
    """

    __name__ = "PhotoOverlay"

    rotation: Optional[float]
    # Adjusts how the photo is placed inside the field of view. This element is
    # useful if your photo has been rotated and deviates slightly from a desired
    # horizontal view.

    view_volume: Optional[ViewVolume]
    # Defines how much of the current scene is visible.

    image_pyramid: Optional[ImagePyramid]
    # Defines the format, resolution, and refresh rate for images that are
    # displayed in the PhotoOverlay.

    point: Optional[Point]
    # Defines the exact coordinates of the PhotoOverlay's origin, in latitude
    # and longitude, and in meters. Latitude and longitude measurements are
    # standard lat-lon projection with WGS84 datum. Altitude is distance above
    # the earth's surface, in meters, and is interpreted according to
    # altitudeMode.

    shape: Optional[Shape]
    # The PhotoOverlay is projected onto the <shape>.
    # The <shape> can be one of the following:
    #   rectangle (default) -
    #       for an ordinary photo
    #   cylinder -
    #       for panoramas, which can be either partial or full cylinders
    #   sphere -
    #       for spherical panoramas

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        visibility: Optional[bool] = None,
        isopen: Optional[bool] = None,
        atom_link: Optional[atom.Link] = None,
        atom_author: Optional[atom.Author] = None,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
        snippet: Optional[Snippet] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[StyleUrl] = None,
        styles: Optional[Iterable[Union[Style, StyleMap]]] = None,
        region: Optional[Region] = None,
        extended_data: Optional[ExtendedData] = None,
        color: Optional[str] = None,
        draw_order: Optional[int] = None,
        icon: Optional[Icon] = None,
        # Photo Overlay specific
        rotation: Optional[float] = None,
        view_volume: Optional[ViewVolume] = None,
        image_pyramid: Optional[ImagePyramid] = None,
        point: Optional[Point] = None,
        shape: Optional[Shape] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            name=name,
            visibility=visibility,
            isopen=isopen,
            atom_link=atom_link,
            atom_author=atom_author,
            address=address,
            phone_number=phone_number,
            snippet=snippet,
            description=description,
            view=view,
            times=times,
            style_url=style_url,
            styles=styles,
            region=region,
            extended_data=extended_data,
            color=color,
            draw_order=draw_order,
            icon=icon,
        )
        self.rotation = rotation
        self.view_volume = view_volume
        self.image_pyramid = image_pyramid
        self.point = point
        self.shape = shape

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self.rotation is not None:
            rotation = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}rotation",
            )
            rotation.text = str(self.rotation)
        if self.view_volume:
            element.append(self.view_volume.etree_element())
        if self.image_pyramid:
            element.append(self.image_pyramid.etree_element())
        if self.point:
            element.append(self.point.etree_element())
        if self.shape:
            shape = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}shape",
            )
            shape.text = self.shape.value
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        rotation = element.find(f"{ns}rotation")
        if rotation is not None:
            kwargs["rotation"] = float(rotation.text)
        view_volume = element.find(f"{ns}ViewVolume")
        if view_volume is not None:
            kwargs["view_volume"] = cast(
                ViewVolume,
                ViewVolume.class_from_element(
                    ns=ns,
                    name_spaces=name_spaces,
                    element=view_volume,
                    strict=strict,
                ),
            )
        image_pyramid = element.find(f"{ns}ImagePyramid")
        if image_pyramid is not None:
            kwargs["image_pyramid"] = cast(
                ImagePyramid,
                ImagePyramid.class_from_element(
                    ns=ns,
                    name_spaces=name_spaces,
                    element=image_pyramid,
                    strict=strict,
                ),
            )
        point = element.find(f"{ns}Point")
        if point is not None:
            kwargs["point"] = cast(
                Point,
                Point.class_from_element(
                    ns=ns,
                    name_spaces=name_spaces,
                    element=point,
                    strict=strict,
                ),
            )
        shape = element.find(f"{ns}shape")
        if shape is not None:
            kwargs["shape"] = Shape(shape.text)
        return kwargs


class LatLonBox(_XMLObject):
    """
    Specifies where the top, bottom, right, and left sides of a bounding box for the
    ground overlay are aligned.
    Also, optionally the rotation of the overlay.

    <north> Specifies the latitude of the north edge of the bounding box,
    in decimal degrees from 0 to ±90.
    <south> Specifies the latitude of the south edge of the bounding box,
    in decimal degrees from 0 to ±90.
    <east> Specifies the longitude of the east edge of the bounding box,
    in decimal degrees from 0 to ±180.
    (For overlays that overlap the meridian of 180° longitude,
    values can extend beyond that range.)
    <west> Specifies the longitude of the west edge of the bounding box,
    in decimal degrees from 0 to ±180.
    (For overlays that overlap the meridian of 180° longitude,
    values can extend beyond that range.)
    <rotation> Specifies a rotation of the overlay about its center, in degrees.
    Values can be ±180. The default is 0 (north).
    Rotations are specified in a counterclockwise direction.
    """

    __name__ = "LatLonBox"
    north: Optional[float]
    south: Optional[float]
    east: Optional[float]
    west: Optional[float]
    rotation: Optional[float]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        north: Optional[float] = None,
        south: Optional[float] = None,
        east: Optional[float] = None,
        west: Optional[float] = None,
        rotation: Optional[float] = None,
    ) -> None:
        super().__init__(ns=ns, name_spaces=name_spaces)
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.rotation = rotation

    def __bool__(self) -> bool:
        return all(
            [
                self.north is not None,
                self.south is not None,
                self.east is not None,
                self.west is not None,
            ],
        )

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        north = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}north",
        )
        north.text = str(self.north)
        south = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}south",
        )
        south.text = str(self.south)
        east = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}east",
        )
        east.text = str(self.east)
        west = config.etree.SubElement(  # type: ignore[attr-defined]
            element,
            f"{self.ns}west",
        )
        west.text = str(self.west)
        if self.rotation is not None:
            rotation = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}rotation",
            )
            rotation.text = str(self.rotation)
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        north = element.find(f"{ns}north")
        if north is not None:
            kwargs["north"] = float(north.text)
        south = element.find(f"{ns}south")
        if south is not None:
            kwargs["south"] = float(south.text)
        east = element.find(f"{ns}east")
        if east is not None:
            kwargs["east"] = float(east.text)
        west = element.find(f"{ns}west")
        if west is not None:
            kwargs["west"] = float(west.text)
        rotation = element.find(f"{ns}rotation")
        if rotation is not None:
            kwargs["rotation"] = float(rotation.text)
        return kwargs


class GroundOverlay(_Overlay):
    """
    This element draws an image overlay draped onto the terrain. The <href>
    child of <Icon> specifies the image to be used as the overlay. This file
    can be either on a local file system or on a web server. If this element
    is omitted or contains no <href>, a rectangle is drawn using the color and
    LatLonBox bounds defined by the ground overlay.

    https://developers.google.com/kml/documentation/kmlreference#groundoverlay
    """

    __name__ = "GroundOverlay"

    altitude: Optional[float]
    # Specifies the distance above the earth's surface, in meters, and is
    # interpreted according to the altitude mode.

    altitude_mode: Optional[AltitudeMode]
    # Specifies how the <altitude> is interpreted. Possible values are:
    #   clampToGround -
    #       (default) Indicates to ignore the altitude specification and drape
    #       the overlay over the terrain.
    #   absolute -
    #       Sets the altitude of the overlay relative to sea level, regardless
    #       of the actual elevation of the terrain beneath the element. For
    #       example, if you set the altitude of an overlay to 10 meters with an
    #       absolute altitude mode, the overlay will appear to be at ground
    #       level if the terrain beneath is also 10 meters above sea level. If
    #       the terrain is 3 meters above sea level, the overlay will appear
    #       elevated above the terrain by 7 meters.

    lat_lon_box: Optional[LatLonBox]
    # Specifies where the top, bottom, right, and left sides of a bounding box
    # for the ground overlay are aligned. Also, optionally the rotation of the
    # overlay.

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        name: Optional[str] = None,
        visibility: Optional[bool] = None,
        isopen: Optional[bool] = None,
        atom_link: Optional[atom.Link] = None,
        atom_author: Optional[atom.Author] = None,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
        snippet: Optional[Snippet] = None,
        description: Optional[str] = None,
        view: Optional[Union[Camera, LookAt]] = None,
        times: Optional[Union[TimeSpan, TimeStamp]] = None,
        style_url: Optional[StyleUrl] = None,
        styles: Optional[Iterable[Union[Style, StyleMap]]] = None,
        region: Optional[Region] = None,
        extended_data: Optional[ExtendedData] = None,
        color: Optional[str] = None,
        draw_order: Optional[int] = None,
        icon: Optional[Icon] = None,
        # Ground Overlay specific
        altitude: Optional[float] = None,
        altitude_mode: Optional[AltitudeMode] = None,
        lat_lon_box: Optional[LatLonBox] = None,
    ) -> None:
        super().__init__(
            ns=ns,
            name_spaces=name_spaces,
            id=id,
            target_id=target_id,
            name=name,
            visibility=visibility,
            isopen=isopen,
            atom_link=atom_link,
            atom_author=atom_author,
            address=address,
            phone_number=phone_number,
            snippet=snippet,
            description=description,
            view=view,
            times=times,
            style_url=style_url,
            styles=styles,
            region=region,
            extended_data=extended_data,
            color=color,
            draw_order=draw_order,
            icon=icon,
        )
        self.altitude = altitude
        self.altitude_mode = altitude_mode
        self.lat_lon_box = lat_lon_box

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)
        if self.altitude:
            altitude = config.etree.SubElement(  # type: ignore[attr-defined]
                element,
                f"{self.ns}altitude",
            )
            altitude.text = str(self.altitude)
            if self.altitude_mode:
                altitude_mode = config.etree.SubElement(  # type: ignore[attr-defined]
                    element,
                    f"{self.ns}altitudeMode",
                )
                altitude_mode.text = self.altitude_mode.value
        if self.lat_lon_box:
            element.append(self.lat_lon_box.etree_element())
        return element

    @classmethod
    def _get_kwargs(
        cls,
        *,
        ns: str,
        name_spaces: Optional[Dict[str, str]] = None,
        element: Element,
        strict: bool,
    ) -> Dict[str, Any]:
        kwargs = super()._get_kwargs(
            ns=ns,
            name_spaces=name_spaces,
            element=element,
            strict=strict,
        )
        altitude = element.find(f"{ns}altitude")
        if altitude is not None:
            kwargs["altitude"] = float(altitude.text)
        altitude_mode = element.find(f"{ns}altitudeMode")
        if altitude_mode is not None:
            kwargs["altitude_mode"] = AltitudeMode(altitude_mode.text)
        lat_lon_box = element.find(f"{ns}LatLonBox")
        if lat_lon_box is not None:
            kwargs["lat_lon_box"] = cast(
                LatLonBox,
                LatLonBox.class_from_element(
                    ns=ns,
                    name_spaces=name_spaces,
                    element=lat_lon_box,
                    strict=strict,
                ),
            )
        return kwargs
