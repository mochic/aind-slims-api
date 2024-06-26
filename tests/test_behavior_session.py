"""Tests methods in mouse module"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from copy import deepcopy

from slims.internal import Record

from aind_slims_api.core import SlimsClient
from aind_slims_api.behavior_session import (
    fetch_behavior_session_content_events,
    write_behavior_session_content_events,
    SlimsBehaviorSessionContentEvent
)

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


class TestBehaviorSession(unittest.TestCase):
    """Tests top level methods in mouse module"""

    example_client: SlimsClient
    example_response: list[Record]
    example_behavior_sessions: list[SlimsBehaviorSessionContentEvent]

    @classmethod
    def setUpClass(cls):
        """Load json files of expected responses from slims"""
        cls.example_client = SlimsClient(
            url="http://fake_url", username="user", password="pass"
        )
        cls.example_response = [
            Record(json_entity=r, slims_api=cls.example_client.db.slims_api)
            for r in json.loads(
                (
                    RESOURCES_DIR /
                    "example_fetch_behavior_sessions_response.json"
                ).read_text()
            )
        ]
        assert len(cls.example_response) > 1, \
            "Example response must be greater than 1 for tests to work..."
        cls.example_behavior_sessions = [
            SlimsBehaviorSessionContentEvent(
                notes="Test notes",
                task_stage="Test stage",
                instrument="Test instrument",
                trainer="Test trainer",
                task="Test task",
                date="2021-01-01",
            ),
            SlimsBehaviorSessionContentEvent(
                notes="Test notes",
                task_stage="Test stage",
                instrument="Test instrument",
                trainer="Test trainer",
                task="Test task",
                date="2021-01-02",
            )
        ]

    @patch("slims.slims.Slims.fetch")
    def test_fetch_behavior_session_content_events_success(
        self,
        mock_fetch: MagicMock
    ):
        """Test fetch_behavior_session_content_events when successful"""
        mock_fetch.return_value = self.example_response
        response = fetch_behavior_session_content_events(
            self.example_client, mouse_name="123456")
        self.assertEqual(
            [item.json_entity for item in self.example_response],
            [item.json_entity for item in response],
        )
        self.assertTrue(response[0].date < response[1].date)

    @patch("logging.Logger.error")
    @patch("slims.slims.Slims.fetch")
    def test_fetch_behavior_session_content_events_validation_fail(
        self, mock_fetch: MagicMock, mock_log_error: MagicMock
    ):
        """Test fetch_behavior_session_content_events when bad values returned"""
        wrong_return = deepcopy(self.example_response)
        wrong_return[0].cnvn_cf_fk_instrument.value = 14
        mock_fetch.return_value = wrong_return
        fetch_behavior_session_content_events(
            self.example_client, mouse_name="123456")
        mock_log_error.assert_called()

    @patch("slims.slims.Slims.add")
    def test_write_behavior_session_content_events_success(
        self, mock_add: MagicMock,
    ):
        """Test write_behavior_session_content_events success"""
        mock_add.return_value = self.example_response
        mouse_name = "123456"
        added = write_behavior_session_content_events(
            self.example_client,
            mouse_name=mouse_name,
            *self.example_behavior_sessions,
        )
        self.assertTrue(
            all((item.mouse_name == mouse_name for item in added))
        )
        self.assertTrue(len(added) == len(self.example_behavior_sessions))

    @patch("logging.Logger.error")
    @patch("slims.slims.Slims.add")
    def test_write_behavior_session_content_events_validation_fail(
        self, mock_add: MagicMock, mock_log_error: MagicMock
    ):
        """Test write_behavior_session_content_events when bad values"""
        mock_add.return_value = None
        bad_behavior_sessions = deepcopy(self.example_behavior_sessions)
        bad_behavior_sessions[0].cnvn_cf_fk_instrument.value = 14
        added = write_behavior_session_content_events(
            self.example_client, mouse_name="123456")
        self.assertTrue(
            (len(bad_behavior_sessions) - 1) == len(added)
        )
        mock_log_error.assert_called()


if __name__ == "__main__":
    unittest.main()
