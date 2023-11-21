# Copyright (C) 2012-2022  Christian Ledermann
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

from typing import Dict
from typing import Optional

from fastkml import config
from fastkml.base import _BaseObject
from fastkml.enums import RefreshMode
from fastkml.enums import Verbosity
from fastkml.enums import ViewRefreshMode
from fastkml.types import Element


class Icon(_BaseObject):
    """
    Represents an <Icon> element used in Overlays.

    Defines an image associated with an Icon style or overlay.
    The required <href> child element defines the location
    of the image to be used as the overlay or as the icon for the placemark.
    This location can either be on a local file system or a remote web server.
    The <gx:x>, <gx:y>, <gx:w>, and <gx:h> elements are used to select one
    icon from an image that contains multiple icons
    (often referred to as an icon palette).
    """

    __name__ = "Icon"

    _href: Optional[str]
    _refresh_mode: Optional[RefreshMode]
    _refresh_interval: Optional[float]
    _view_refresh_mode: Optional[ViewRefreshMode]
    _view_refresh_time: Optional[float]
    _view_bound_scale: Optional[float]
    _view_format: Optional[str]
    _http_query: Optional[str]

    def __init__(
        self,
        ns: Optional[str] = None,
        name_spaces: Optional[Dict[str, str]] = None,
        id: Optional[str] = None,
        target_id: Optional[str] = None,
        href: Optional[str] = None,
        refresh_mode: Optional[RefreshMode] = None,
        refresh_interval: Optional[float] = None,
        view_refresh_mode: Optional[ViewRefreshMode] = None,
        view_refresh_time: Optional[float] = None,
        view_bound_scale: Optional[float] = None,
        view_format: Optional[str] = None,
        http_query: Optional[str] = None,
    ) -> None:
        """Initialize the KML Icon Object."""
        super().__init__(ns=ns, name_spaces=name_spaces, id=id, target_id=target_id)
        self._href = href
        self._refresh_mode = refresh_mode
        self._refresh_interval = refresh_interval
        self._view_refresh_mode = view_refresh_mode
        self._view_refresh_time = view_refresh_time
        self._view_bound_scale = view_bound_scale
        self._view_format = view_format
        self._http_query = http_query

    @property
    def href(self) -> Optional[str]:
        """An HTTP address or a local file specification used to load an icon."""
        return self._href

    @href.setter
    def href(self, href) -> None:
        if isinstance(href, str):
            self._href = href
        elif href is None:
            self._href = None
        else:
            raise ValueError

    @property
    def refresh_mode(self) -> Optional[RefreshMode]:
        """
        Specifies a time-based refresh mode.

        Can be one of the following:
          - onChange - refresh when the file is loaded and whenever the Link
            parameters change (the default).
          - onInterval - refresh every n seconds (specified in <refreshInterval>).
          - onExpire - refresh the file when the expiration time is reached.
        """
        return self._refresh_mode

    @refresh_mode.setter
    def refresh_mode(self, refresh_mode: Optional[RefreshMode]) -> None:
        self._refresh_mode = refresh_mode

    @property
    def refresh_interval(self) -> Optional[float]:
        """Indicates to refresh the file every n seconds."""
        return self._refresh_interval

    @refresh_interval.setter
    def refresh_interval(self, refresh_interval: Optional[float]) -> None:
        if isinstance(refresh_interval, float):
            self._refresh_interval = refresh_interval
        elif refresh_interval is None:
            self._refresh_interval = None
        else:
            raise ValueError

    @property
    def view_refresh_mode(self) -> Optional[ViewRefreshMode]:
        """
        Specifies how the link is refreshed when the "camera" changes.

        Can be one of the following:
         - never (default) - Ignore changes in the view.
           Also ignore <viewFormat> parameters, if any.
         - onStop - Refresh the file n seconds after movement stops,
           where n is specified in <viewRefreshTime>.
         - onRequest - Refresh the file only when the user explicitly requests it.
           (For example, in Google Earth, the user right-clicks and selects Refresh
            in the Context menu.)
         - onRegion - Refresh the file when the Region becomes active.
        """
        return self._view_refresh_mode

    @view_refresh_mode.setter
    def view_refresh_mode(self, view_refresh_mode: Optional[ViewRefreshMode]) -> None:
        self._view_refresh_mode = view_refresh_mode

    @property
    def view_refresh_time(self):
        """
        After camera movement stops, specifies the number of seconds to
        wait before refreshing the view.
        """
        return self._view_refresh_time

    @view_refresh_time.setter
    def view_refresh_time(self, view_refresh_time: Optional[float]) -> None:
        if isinstance(view_refresh_time, float):
            self._view_refresh_time = view_refresh_time
        elif view_refresh_time is None:
            self._view_refresh_time = None
        else:
            raise ValueError

    @property
    def view_bound_scale(self) -> Optional[float]:
        """
        Scales the BBOX parameters before sending them to the server.

        A value less than 1 specifies to use less than the full view (screen).
        A value greater than 1 specifies to fetch an area that extends beyond
        the edges of the current view.
        """
        return self._view_bound_scale

    @view_bound_scale.setter
    def view_bound_scale(self, view_bound_scale: Optional[float]) -> None:
        if isinstance(view_bound_scale, float):
            self._view_bound_scale = view_bound_scale
        elif view_bound_scale is None:
            self._view_bound_scale = None
        else:
            raise ValueError

    @property
    def view_format(self):
        """
        Specifies the format of the query string that is appended to the
        Link's <href> before the file is fetched.
        (If the <href> specifies a local file, this element is ignored.).

        This information matches the Web Map Service (WMS) bounding box specification.
        If you specify an empty <viewFormat> tag, no information is appended to the
        query string.
        You can also specify a custom set of viewing parameters to add to the query
        string. If you supply a format string, it is used instead of the BBOX
        information. If you also want the BBOX information, you need to add those
        parameters along with the custom parameters.
        You can use any of the following parameters in your format string:
         - [lookatLon], [lookatLat] - longitude and latitude of the point that
           <LookAt> is viewing
         - [lookatRange], [lookatTilt], [lookatHeading] - values used by the
           <LookAt> element (see descriptions of <range>, <tilt>, and <heading>
           in <LookAt>)
         - [lookatTerrainLon], [lookatTerrainLat], [lookatTerrainAlt] - point on the
           terrain in degrees/meters that <LookAt> is viewing
         - [cameraLon], [cameraLat], [cameraAlt] - degrees/meters of the eyepoint for
           the camera
         - [horizFov], [vertFov] - horizontal, vertical field of view for the camera
         - [horizPixels], [vertPixels] - size in pixels of the 3D viewer
         - [terrainEnabled] - indicates whether the 3D viewer is showing terrain (1)
           or not (0)
        """
        return self._view_format

    @view_format.setter
    def view_format(self, view_format) -> None:
        if isinstance(view_format, str):
            self._view_format = view_format
        elif view_format is None:
            self._view_format = None
        else:
            raise ValueError

    @property
    def http_query(self):
        """
        Appends information to the query string, based on the parameters specified.

        The following parameters are supported:
         - [clientVersion]
         - [kmlVersion]
         - [clientName]
         - [language]
        """
        return self._http_query

    @http_query.setter
    def http_query(self, http_query) -> None:
        if isinstance(http_query, str):
            self._http_query = http_query
        elif http_query is None:
            self._http_query = None
        else:
            raise ValueError

    def etree_element(
        self,
        precision: Optional[int] = None,
        verbosity: Verbosity = Verbosity.normal,
    ) -> Element:
        element = super().etree_element(precision=precision, verbosity=verbosity)

        if self._href:
            href = config.etree.SubElement(element, f"{self.ns}href")
            href.text = self._href
        if self._refresh_mode:
            refresh_mode = config.etree.SubElement(element, f"{self.ns}refreshMode")
            refresh_mode.text = self._refresh_mode.value
        if self._refresh_interval:
            refresh_interval = config.etree.SubElement(
                element,
                f"{self.ns}refreshInterval",
            )
            refresh_interval.text = str(self._refresh_interval)
        if self._view_refresh_mode:
            view_refresh_mode = config.etree.SubElement(
                element,
                f"{self.ns}viewRefreshMode",
            )
            view_refresh_mode.text = self._view_refresh_mode.value
        if self._view_refresh_time:
            view_refresh_time = config.etree.SubElement(
                element,
                f"{self.ns}viewRefreshTime",
            )
            view_refresh_time.text = str(self._view_refresh_time)
        if self._view_bound_scale:
            view_bound_scale = config.etree.SubElement(
                element,
                f"{self.ns}viewBoundScale",
            )
            view_bound_scale.text = str(self._view_bound_scale)
        if self._view_format:
            view_format = config.etree.SubElement(element, f"{self.ns}viewFormat")
            view_format.text = self._view_format
        if self._http_query:
            http_query = config.etree.SubElement(element, f"{self.ns}httpQuery")
            http_query.text = self._http_query

        return element

    def from_element(self, element: Element) -> None:
        super().from_element(element)

        href = element.find(f"{self.ns}href")
        if href is not None:
            self.href = href.text

        refresh_mode = element.find(f"{self.ns}refreshMode")
        if refresh_mode is not None:
            self.refresh_mode = RefreshMode(refresh_mode.text)

        refresh_interval = element.find(f"{self.ns}refreshInterval")
        if refresh_interval is not None:
            try:
                self.refresh_interval = float(refresh_interval.text)
            except ValueError:
                self.refresh_interval = None

        view_refresh_mode = element.find(f"{self.ns}viewRefreshMode")
        if view_refresh_mode is not None:
            self.view_refresh_mode = ViewRefreshMode(view_refresh_mode.text)

        view_refresh_time = element.find(f"{self.ns}viewRefreshTime")
        if view_refresh_time is not None:
            try:
                self.view_refresh_time = float(view_refresh_time.text)
            except ValueError:
                self.view_refresh_time = None

        view_bound_scale = element.find(f"{self.ns}viewBoundScale")
        if view_bound_scale is not None:
            try:
                self.view_bound_scale = float(view_bound_scale.text)
            except ValueError:
                self.view_bound_scale = None

        view_format = element.find(f"{self.ns}viewFormat")
        if view_format is not None:
            self.view_format = view_format.text

        http_query = element.find(f"{self.ns}httpQuery")
        if http_query is not None:
            self.http_query = http_query.text
