# Copyright (C) 2021 - 2022  Christian Ledermann
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

"""Test the Network Link Control classes."""

import datetime

from dateutil.tz import tzutc

from fastkml import views
from fastkml.containers import Folder
from fastkml.features import Placemark
from fastkml.network_link_control import Change
from fastkml.network_link_control import Create
from fastkml.network_link_control import Delete
from fastkml.network_link_control import NetworkLinkControl
from fastkml.network_link_control import Update
from fastkml.times import KmlDateTime
from tests.base import Lxml
from tests.base import Pyuppsala
from tests.base import StdLibrary


class TestStdLibrary(StdLibrary):
    """Test with the standard library."""

    def test_network_link_control_obj(self) -> None:
        dt = datetime.datetime.now(tz=tzutc())
        kml_datetime = KmlDateTime(dt=dt)
        view = views.Camera()

        network_control_obj = NetworkLinkControl(
            min_refresh_period=1.1,
            max_session_length=100.1,
            cookie="cookie",
            message="message",
            link_name="link_name",
            link_description="link_description",
            link_snippet="link_snippet",
            expires=kml_datetime,
            view=view,
        )

        assert network_control_obj.min_refresh_period == 1.1
        assert network_control_obj.max_session_length == 100.1
        assert network_control_obj.cookie == "cookie"
        assert network_control_obj.message == "message"
        assert network_control_obj.link_name == "link_name"
        assert network_control_obj.link_description == "link_description"
        assert network_control_obj.link_snippet == "link_snippet"
        assert str(network_control_obj.expires) == str(kml_datetime)
        assert str(network_control_obj.view) == str(view)

    def test_network_link_control_kml(self) -> None:
        doc = (
            '<kml:NetworkLinkControl xmlns:kml="http://www.opengis.net/kml/2.2">'
            "<kml:minRefreshPeriod>432000</kml:minRefreshPeriod>"
            "<kml:maxSessionLength>-1</kml:maxSessionLength>"
            "<kml:linkSnippet>A Snippet</kml:linkSnippet>"
            "<kml:expires>2008-05-30</kml:expires>"
            "</kml:NetworkLinkControl>"
        )

        nc = NetworkLinkControl.from_string(doc)

        dt = datetime.date(2008, 5, 30)
        kml_datetime = KmlDateTime(dt=dt)

        nc_obj = NetworkLinkControl(
            min_refresh_period=432000,
            max_session_length=-1,
            link_snippet="A Snippet",
            expires=kml_datetime,
        )

        assert nc == nc_obj

    def test_update_obj(self) -> None:
        """Test Update object creation."""
        placemark = Placemark(id="pm1", target_id="pm1", name="Test Placemark")
        change = Change(objects=[placemark])
        update = Update(
            target_href="http://example.com/target.kml",
            operations=[change],
        )

        assert update.target_href == "http://example.com/target.kml"
        assert len(update.operations) == 1
        assert isinstance(update.operations[0], Change)
        assert len(update.operations[0].objects) == 1
        obj = update.operations[0].objects[0]
        assert isinstance(obj, Placemark)
        assert obj.name == "Test Placemark"

    def test_update_with_create(self) -> None:
        """Test Update with Create action."""
        # Create can only contain containers (Document, Folder) per the schema
        folder = Folder(id="new_folder", name="New Folder")
        create = Create(objects=[folder])
        update = Update(
            target_href="http://example.com/target.kml",
            operations=[create],
        )

        assert update.target_href == "http://example.com/target.kml"
        assert len(update.operations) == 1
        assert isinstance(update.operations[0], Create)
        assert len(update.operations[0].objects) == 1

    def test_update_with_delete(self) -> None:
        """Test Update with Delete action."""
        placemark = Placemark(target_id="delete_pm")
        delete = Delete(objects=[placemark])
        update = Update(
            target_href="http://example.com/target.kml",
            operations=[delete],
        )

        assert update.target_href == "http://example.com/target.kml"
        assert len(update.operations) == 1
        assert isinstance(update.operations[0], Delete)
        assert len(update.operations[0].objects) == 1

    def test_update_with_multiple_operations(self) -> None:
        """Test Update with multiple operations in order."""
        folder = Folder(id="new_folder", name="New Folder")
        create = Create(objects=[folder])

        placemark = Placemark(target_id="pm1", name="Updated Name")
        change = Change(objects=[placemark])

        delete_placemark = Placemark(target_id="pm2")
        delete = Delete(objects=[delete_placemark])

        update = Update(
            target_href="http://example.com/target.kml",
            operations=[create, change, delete],
        )

        assert update.target_href == "http://example.com/target.kml"
        assert len(update.operations) == 3
        assert isinstance(update.operations[0], Create)
        assert isinstance(update.operations[1], Change)
        assert isinstance(update.operations[2], Delete)

    def test_network_link_control_with_update(self) -> None:
        """Test NetworkLinkControl with Update."""
        placemark = Placemark(id="pm1", target_id="pm1", name="Updated Placemark")
        change = Change(objects=[placemark])
        update = Update(
            target_href="http://example.com/target.kml",
            operations=[change],
        )
        nlc = NetworkLinkControl(update=update)

        assert nlc.update is not None
        assert nlc.update.target_href == "http://example.com/target.kml"
        assert len(nlc.update.operations) == 1
        assert isinstance(nlc.update.operations[0], Change)

    def test_update_kml_roundtrip(self) -> None:
        """Test Update serialization and parsing roundtrip."""
        placemark = Placemark(id="pm1", target_id="pm1", name="Updated Placemark")
        change = Change(objects=[placemark])
        update = Update(
            target_href="http://example.com/target.kml",
            operations=[change],
        )
        nlc = NetworkLinkControl(update=update)

        # Serialize
        kml_string = nlc.to_string()

        # Parse back
        parsed_nlc = NetworkLinkControl.from_string(kml_string)

        assert parsed_nlc.update is not None
        assert parsed_nlc.update.target_href == "http://example.com/target.kml"
        assert len(parsed_nlc.update.operations) == 1
        assert isinstance(parsed_nlc.update.operations[0], Change)
        obj = parsed_nlc.update.operations[0].objects[0]
        assert isinstance(obj, Placemark)
        assert obj.name == "Updated Placemark"

    def test_update_kml_parsing(self) -> None:
        """Test parsing Update from KML string."""
        doc = """
        <kml:NetworkLinkControl xmlns:kml="http://www.opengis.net/kml/2.2">
          <kml:Update>
            <kml:targetHref>http://example.com/target.kml</kml:targetHref>
            <kml:Change>
              <kml:Placemark targetId="pm1">
                <kml:name>Changed Name</kml:name>
              </kml:Placemark>
            </kml:Change>
          </kml:Update>
        </kml:NetworkLinkControl>
        """

        nlc = NetworkLinkControl.from_string(doc)

        assert nlc.update is not None
        assert nlc.update.target_href == "http://example.com/target.kml"
        assert len(nlc.update.operations) == 1
        assert isinstance(nlc.update.operations[0], Change)
        obj = nlc.update.operations[0].objects[0]
        assert isinstance(obj, Placemark)
        assert obj.name == "Changed Name"
        assert obj.target_id == "pm1"


class TestLxml(Lxml, TestStdLibrary):
    """Test with lxml."""


class TestPyuppsala(Pyuppsala, TestStdLibrary):
    """Test with pyuppsala."""
