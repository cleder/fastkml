# Copyright (C) 2023  Christian Ledermann
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
"""Overlays."""

import logging
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Union

from fastkml import atom
from fastkml import config
from fastkml import gx
from fastkml.base import _XMLObject
from fastkml.data import ExtendedData
from fastkml.enums import AltitudeMode
from fastkml.enums import GridOrigin
from fastkml.enums import Shape
from fastkml.features import Snippet
from fastkml.features import _Feature
from fastkml.geometry import LinearRing
from fastkml.geometry import LineString
from fastkml.geometry import MultiGeometry
from fastkml.geometry import Point
from fastkml.geometry import Polygon
from fastkml.helpers import enum_subelement
from fastkml.helpers import float_subelement
from fastkml.helpers import int_subelement
from fastkml.helpers import subelement_enum_kwarg
from fastkml.helpers import subelement_float_kwarg
from fastkml.helpers import subelement_int_kwarg
from fastkml.helpers import subelement_text_kwarg
from fastkml.helpers import text_subelement
from fastkml.helpers import xml_subelement
from fastkml.helpers import xml_subelement_kwarg
from fastkml.links import Icon
from fastkml.registry import RegistryItem
from fastkml.registry import registry
from fastkml.styles import Style
from fastkml.styles import StyleMap
from fastkml.styles import StyleUrl
from fastkml.times import TimeSpan
from fastkml.times import TimeStamp
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

    color: Optional[str]
    # Color values expressed in hexadecimal notation, including opacity (alpha)
    # values. The order of expression is alphaOverlay, blue, green, red
    # (AABBGGRR). The range of values for any one color is 0 to 255 (00 to ff).
    # For opacity, 00 is fully transparent and ff is fully opaque.

    draw_order: Optional[int]
    # Defines the stacking order for the images in overlapping overlays.
    # Overlays with higher <drawOrder> values are drawn on top of those with
    # lower <drawOrder> values.

    icon: Optional[Icon]
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
        """
        Initialize an Overlay object.

        Parameters
        ----------
        ns : Optional[str]
            The namespace of the element.
        name_spaces : Optional[Dict[str, str]]
            The dictionary of namespace prefixes and URIs.
        id : Optional[str]
            The ID of the element.
        target_id : Optional[str]
            The target ID of the element.
        name : Optional[str]
            The name of the element.
        visibility : Optional[bool]
            The visibility of the element.
        isopen : Optional[bool]
            The open state of the element.
        atom_link : Optional[atom.Link]
            The Atom link associated with the element.
        atom_author : Optional[atom.Author]
            The Atom author associated with the element.
        address : Optional[str]
            The address associated with the element.
        phone_number : Optional[str]
            The phone number associated with the element.
        snippet : Optional[Snippet]
            The snippet associated with the element.
        description : Optional[str]
            The description of the element.
        view : Optional[Union[Camera, LookAt]]
            The view associated with the element.
        times : Optional[Union[TimeSpan, TimeStamp]]
            The times associated with the element.
        style_url : Optional[StyleUrl]
            The style URL associated with the element.
        styles : Optional[Iterable[Union[Style, StyleMap]]]
            The styles associated with the element.
        region : Optional[Region]
            The region associated with the element.
        extended_data : Optional[ExtendedData]
            The extended data associated with the element.
        color : Optional[str]
            The color of the overlay.
        draw_order : Optional[int]
            The draw order of the overlay.
        icon : Optional[Icon]
            The icon associated with the overlay.

        Returns
        -------
        None

        """
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
        self.icon = icon
        self.color = color
        self.draw_order = draw_order

    def __repr__(self) -> str:
        """Create a string (c)representation for _Overlay."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"visibility={self.visibility!r}, "
            f"isopen={self.isopen!r}, "
            f"atom_link={self.atom_link!r}, "
            f"atom_author={self.atom_author!r}, "
            f"address={self.address!r}, "
            f"phone_number={self.phone_number!r}, "
            f"snippet={self.snippet!r}, "
            f"description={self.description!r}, "
            f"view={self.view!r}, "
            f"times={self.times!r}, "
            f"style_url={self.style_url!r}, "
            f"styles={self.styles!r}, "
            f"region={self.region!r}, "
            f"extended_data={self.extended_data!r}, "
            f"color={self.color!r}, "
            f"draw_order={self.draw_order!r}, "
            f"icon={self.icon!r}, "
            ")"
        )


registry.register(
    _Overlay,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="color",
        node_name="color",
        classes=(str,),
        get_kwarg=subelement_text_kwarg,
        set_element=text_subelement,
    ),
)
registry.register(
    _Overlay,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="draw_order",
        node_name="drawOrder",
        classes=(int,),
        get_kwarg=subelement_int_kwarg,
        set_element=int_subelement,
    ),
)
registry.register(
    _Overlay,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="icon",
        node_name="Icon",
        classes=(Icon,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)


class ViewVolume(_XMLObject):
    """
    The ViewVolume defines how much of the current scene is visible.

    Specifying the field of view is analogous to specifying the lens opening in a
    physical camera.
    A small field of view, like a telephoto lens, focuses on a small part of the scene.
    A large field of view, like a wide-angle lens, focuses on a large part of the scene.

    https://developers.google.com/kml/documentation/kmlreference#viewvolume
    """

    _default_nsid = config.KML

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
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new Overlay object.

        Parameters
        ----------
        ns : Optional[str]
            The namespace for the Overlay element. Defaults to None.
        name_spaces : Optional[Dict[str, str]]
            A dictionary of namespace prefixes and URIs. Defaults to None.
        left_fov : Optional[float]
            The left field of view angle in degrees. Defaults to None.
        right_fov : Optional[float]
            The right field of view angle in degrees. Defaults to None.
        bottom_fov : Optional[float]
            The bottom field of view angle in degrees. Defaults to None.
        top_fov : Optional[float]
            The top field of view angle in degrees. Defaults to None.
        near : Optional[float]
            The near clipping distance in meters. Defaults to None.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        None

        """
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.left_fov = left_fov
        self.right_fov = right_fov
        self.bottom_fov = bottom_fov
        self.top_fov = top_fov
        self.near = near

    def __repr__(self) -> str:
        """Create a string (c)representation for ViewVolume."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"left_fov={self.left_fov!r}, "
            f"right_fov={self.right_fov!r}, "
            f"bottom_fov={self.bottom_fov!r}, "
            f"top_fov={self.top_fov!r}, "
            f"near={self.near!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if all the required attributes are not None.

        Returns
        -------
            bool: True if all the required attributes are not None, False otherwise.

        """
        return all(
            [
                self.left_fov is not None,
                self.right_fov is not None,
                self.bottom_fov is not None,
                self.top_fov is not None,
                self.near is not None,
            ],
        )


registry.register(
    ViewVolume,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="left_fov",
        node_name="leftFov",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    ViewVolume,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="right_fov",
        node_name="rightFov",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    ViewVolume,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="bottom_fov",
        node_name="bottomFov",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    ViewVolume,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="top_fov",
        node_name="topFov",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    ViewVolume,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="near",
        node_name="near",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)


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

    _default_nsid = config.KML

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
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new Overlay object.

        Parameters
        ----------
        ns : Optional[str]
            The namespace for the overlay.
        name_spaces : Optional[Dict[str, str]]
            A dictionary of namespace prefixes and URIs.
        tile_size : Optional[int]
            The size of each tile in pixels.
        max_width : Optional[int]
            The maximum width of the overlay.
        max_height : Optional[int]
            The maximum height of the overlay.
        grid_origin : Optional[GridOrigin]
            The origin of the grid.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        None

        """
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.tile_size = tile_size
        self.max_width = max_width
        self.max_height = max_height
        self.grid_origin = grid_origin

    def __repr__(self) -> str:
        """Create a string (c)representation for ImagePyramid."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"tile_size={self.tile_size!r}, "
            f"max_width={self.max_width!r}, "
            f"max_height={self.max_height!r}, "
            f"grid_origin={self.grid_origin}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if the overlay has all the required attributes set.

        Returns
        -------
            bool: True if all the required attributes are set, False otherwise.

        """
        return (
            self.tile_size is not None
            and self.max_width is not None
            and self.max_height is not None
            and self.grid_origin is not None
        )


registry.register(
    ImagePyramid,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="tile_size",
        node_name="tileSize",
        classes=(int,),
        get_kwarg=subelement_int_kwarg,
        set_element=int_subelement,
    ),
)
registry.register(
    ImagePyramid,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="max_width",
        node_name="maxWidth",
        classes=(int,),
        get_kwarg=subelement_int_kwarg,
        set_element=int_subelement,
    ),
)
registry.register(
    ImagePyramid,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="max_height",
        node_name="maxHeight",
        classes=(int,),
        get_kwarg=subelement_int_kwarg,
        set_element=int_subelement,
    ),
)
registry.register(
    ImagePyramid,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="grid_origin",
        node_name="gridOrigin",
        classes=(GridOrigin,),
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
    ),
)


class PhotoOverlay(_Overlay):
    """
    PhotoOverlays are photographs that are directly embedded in the Earth's landscape.

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
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new Overlay object.

        Args:
        ----
            ns : Optional[str]
                The namespace for the element.
            name_spaces : Optional[Dict[str, str]]
                The dictionary of namespace prefixes and URIs.
            id : Optional[str]
                The ID of the element.
            target_id : Optional[str]
                The target ID of the element.
            name : Optional[str]
                The name of the element.
            visibility : Optional[bool]
                The visibility of the element.
            isopen : Optional[bool]
                The open status of the element.
            atom_link : Optional[atom.Link]
                The Atom link associated with the element.
            atom_author : Optional[atom.Author]
                The Atom author associated with the element.
            address : Optional[str]
                The address associated with the element.
            phone_number : Optional[str]
                The phone number associated with the element.
            snippet : Optional[Snippet]
                The snippet associated with the element.
            description : Optional[str]
                The description of the element.
            view : Optional[Union[Camera, LookAt]]
                The view associated with the element.
            times : Optional[Union[TimeSpan, TimeStamp]]
                The times associated with the element.
            style_url : Optional[StyleUrl]
                The style URL associated with the element.
            styles : Optional[Iterable[Union[Style, StyleMap]]]
                The styles associated with the element.
            region : Optional[Region]
                The region associated with the element.
            extended_data : Optional[ExtendedData]
                The extended data associated with the element.
            color : Optional[str]
                The color associated with the element.
            draw_order : Optional[int]
                The draw order of the element.
            icon : Optional[Icon]
                The icon associated with the element.
            rotation : Optional[float]
                The rotation of the element (specific to Photo Overlay).
            view_volume : Optional[ViewVolume]
                The view volume of the element (specific to Photo Overlay).
            image_pyramid : Optional[ImagePyramid]
                The image pyramid of the element (specific to Photo Overlay).
            point : Optional[Point]
                The point associated with the element (specific to Photo Overlay).
            shape : Optional[Shape]
                The shape associated with the element (specific to Photo Overlay).
            kwargs : Any
                Additional keyword arguments.

        Returns:
        -------
            None

        """
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
            **kwargs,
        )
        self.rotation = rotation
        self.view_volume = view_volume
        self.image_pyramid = image_pyramid
        self.point = point
        self.shape = shape

    def __repr__(self) -> str:
        """Create a string (c)representation for PhotoOverlay."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"visibility={self.visibility!r}, "
            f"isopen={self.isopen!r}, "
            f"atom_link={self.atom_link!r}, "
            f"atom_author={self.atom_author!r}, "
            f"address={self.address!r}, "
            f"phone_number={self.phone_number!r}, "
            f"snippet={self.snippet!r}, "
            f"description={self.description!r}, "
            f"view={self.view!r}, "
            f"times={self.times!r}, "
            f"style_url={self.style_url!r}, "
            f"styles={self.styles!r}, "
            f"region={self.region!r}, "
            f"extended_data={self.extended_data!r}, "
            f"color={self.color!r}, "
            f"draw_order={self.draw_order!r}, "
            f"icon={self.icon!r}, "
            f"rotation={self.rotation!r}, "
            f"view_volume={self.view_volume!r}, "
            f"image_pyramid={self.image_pyramid!r}, "
            f"point={self.point!r}, "
            f"shape={self.shape}, "
            f"**{self._get_splat()!r},"
            ")"
        )


registry.register(
    PhotoOverlay,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="rotation",
        node_name="rotation",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    PhotoOverlay,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="view_volume",
        node_name="ViewVolume",
        classes=(ViewVolume,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    PhotoOverlay,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="image_pyramid",
        node_name="ImagePyramid",
        classes=(ImagePyramid,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    PhotoOverlay,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="point",
        node_name="Point",
        classes=(Point,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
registry.register(
    PhotoOverlay,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="shape",
        node_name="shape",
        classes=(Shape,),
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
    ),
)


class LatLonBox(_XMLObject):
    """
    Specifies the top, bottom, right, and left sides of a bounding box for an overlay.

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

    _default_nsid = config.KML

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
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new Overlay object.

        Args:
        ----
            ns : Optional[str]
                The namespace for the Overlay element.
            name_spaces : Optional[Dict[str, str]]
                A dictionary of namespace prefixes and URIs.
            north : Optional[float]
                The northern latitude of the Overlay's bounding box.
            south : Optional[float]
                The southern latitude of the Overlay's bounding box.
            east : Optional[float]
                The eastern longitude of the Overlay's bounding box.
            west : Optional[float]
                The western longitude of the Overlay's bounding box.
            rotation : Optional[float]
                The rotation angle of the Overlay.
            **kwargs : Any
                Additional keyword arguments.

        Returns:
        -------
         None

        """
        super().__init__(ns=ns, name_spaces=name_spaces, **kwargs)
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.rotation = rotation

    def __repr__(self) -> str:
        """Create a string (c)representation for LatLonBox."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"north={self.north!r}, "
            f"south={self.south!r}, "
            f"east={self.east!r}, "
            f"west={self.west!r}, "
            f"rotation={self.rotation!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )

    def __bool__(self) -> bool:
        """
        Check if all the attributes necessary for bounding box calculation are not None.

        Returns
        -------
            bool: True if all attributes (north, south, east, west) are not None.

        """
        return all(
            [
                self.north is not None,
                self.south is not None,
                self.east is not None,
                self.west is not None,
            ],
        )


registry.register(
    LatLonBox,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="north",
        node_name="north",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    LatLonBox,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="south",
        node_name="south",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    LatLonBox,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="east",
        node_name="east",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    LatLonBox,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="west",
        node_name="west",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    LatLonBox,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="rotation",
        node_name="rotation",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)


class GroundOverlay(_Overlay):
    """
    Draw an image overlay draped onto the terrain.

    The <href> child of <Icon> specifies the image to be used as the overlay. This file
    can be either on a local file system or on a web server. If this element
    is omitted or contains no <href>, a rectangle is drawn using the color and
    LatLonBox bounds defined by the ground overlay.

    https://developers.google.com/kml/documentation/kmlreference#groundoverlay
    """

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
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new Overlay object.

        Args:
        ----
        ns : Optional[str]
            The namespace of the element.
        name_spaces : Optional[Dict[str, str]]
            The dictionary of namespace prefixes and URIs.
        id : Optional[str]
            The ID of the element.
        target_id : Optional[str]
            The target ID of the element.
        name : Optional[str]
            The name of the element.
        visibility : Optional[bool]
            The visibility of the element.
        isopen : Optional[bool]
            The open state of the element.
        atom_link : Optional[atom.Link]
            The Atom link associated with the element.
        atom_author : Optional[atom.Author]
            The Atom author associated with the element.
        address : Optional[str]
            The address of the element.
        phone_number : Optional[str]
            The phone number of the element.
        snippet : Optional[Snippet]
            The snippet associated with the element.
        description : Optional[str]
            The description of the element.
        view : Optional[Union[Camera, LookAt]]
            The view associated with the element.
        times : Optional[Union[TimeSpan, TimeStamp]]
            The times associated with the element.
        style_url : Optional[StyleUrl]
            The style URL of the element.
        styles : Optional[Iterable[Union[Style, StyleMap]]]
            The styles associated with the element.
        region : Optional[Region]
            The region associated with the element.
        extended_data : Optional[ExtendedData]
            The extended data associated with the element.
        color : Optional[str]
            The color of the element.
        draw_order : Optional[int]
            The draw order of the element.
        icon : Optional[Icon]
            The icon associated with the element.
        altitude : Optional[float]
            The altitude of the element.
        altitude_mode : Optional[AltitudeMode]
            The altitude mode of the element.
        lat_lon_box : Optional[LatLonBox]
            The latitude-longitude box associated with the element.
        kwargs : Any
            Additional keyword arguments.

        Returns:
        -------
        None

        """
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
            **kwargs,
        )
        self.altitude = altitude
        self.altitude_mode = altitude_mode
        self.lat_lon_box = lat_lon_box

    def __repr__(self) -> str:
        """Create a string (c)representation for GroundOverlay."""
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}("
            f"ns={self.ns!r}, "
            f"name_spaces={self.name_spaces!r}, "
            f"id={self.id!r}, "
            f"target_id={self.target_id!r}, "
            f"name={self.name!r}, "
            f"visibility={self.visibility!r}, "
            f"isopen={self.isopen!r}, "
            f"atom_link={self.atom_link!r}, "
            f"atom_author={self.atom_author!r}, "
            f"address={self.address!r}, "
            f"phone_number={self.phone_number!r}, "
            f"snippet={self.snippet!r}, "
            f"description={self.description!r}, "
            f"view={self.view!r}, "
            f"times={self.times!r}, "
            f"style_url={self.style_url!r}, "
            f"styles={self.styles!r}, "
            f"region={self.region!r}, "
            f"extended_data={self.extended_data!r}, "
            f"color={self.color!r}, "
            f"draw_order={self.draw_order!r}, "
            f"icon={self.icon!r}, "
            f"altitude={self.altitude!r}, "
            f"altitude_mode={self.altitude_mode}, "
            f"lat_lon_box={self.lat_lon_box!r}, "
            f"**{self._get_splat()!r},"
            ")"
        )


registry.register(
    GroundOverlay,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="altitude",
        node_name="altitude",
        classes=(float,),
        get_kwarg=subelement_float_kwarg,
        set_element=float_subelement,
    ),
)
registry.register(
    GroundOverlay,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="altitude_mode",
        node_name="altitudeMode",
        classes=(AltitudeMode,),
        get_kwarg=subelement_enum_kwarg,
        set_element=enum_subelement,
    ),
)
registry.register(
    GroundOverlay,
    RegistryItem(
        ns_ids=("kml",),
        attr_name="lat_lon_box",
        node_name="LatLonBox",
        classes=(LatLonBox,),
        get_kwarg=xml_subelement_kwarg,
        set_element=xml_subelement,
    ),
)
