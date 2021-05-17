"""
Unit test for Utils
"""

import os
from unittest import TestCase
from unittest.mock import patch, Mock

from samcli.local.docker.utils import to_posix_path, find_free_port
from samcli.local.docker.exceptions import NoFreePortsError


class TestPosixPath(TestCase):
    def setUp(self):
        self.ntpath = "C:\\Users\\UserName\\AppData\\Local\\Temp\\temp1337"
        self.posixpath = "/c/Users/UserName/AppData/Local/Temp/temp1337"
        self.current_working_dir = os.getcwd()

    @patch("samcli.local.docker.utils.os")
    def test_convert_posix_path_if_windows_style_path(self, mock_os):
        mock_os.name = "nt"
        self.assertEqual(self.posixpath, to_posix_path(self.ntpath))

    @patch("samcli.local.docker.utils.os")
    def test_do_not_convert_posix_path(self, mock_os):
        mock_os.name = "posix"
        self.assertEqual(self.current_working_dir, to_posix_path(self.current_working_dir))


class TestFreePorts(TestCase):
    @patch("samcli.local.docker.utils.socket")
    @patch("samcli.local.docker.utils.random")
    def test_free_port_first_attempt(self, mock_random, mock_socket):
        mock_random.randrange = Mock(side_effect=[3093] * 1000)
        port = find_free_port(start=3000, end=4000)
        self.assertEqual(port, 3093)

    @patch("samcli.local.docker.utils.socket")
    @patch("samcli.local.docker.utils.random")
    def test_free_port_after_failed_attempts(self, mock_random, mock_socket_module):
        mock_socket_object = Mock()
        mock_socket_object.bind = Mock(side_effect=[OSError, OSError, Mock()])
        mock_socket_module.socket = Mock(return_value=mock_socket_object)
        mock_random.randrange = Mock(side_effect=[3093, 3987, 3300, 3033] * 250)
        port = find_free_port(start=3000, end=4000)
        self.assertEqual(port, 3300)

    @patch("samcli.local.docker.utils.socket")
    @patch("samcli.local.docker.utils.random")
    def test_no_free_port_after_failed_attempts(self, mock_random, mock_socket_module):
        mock_socket_object = Mock()
        mock_socket_object.bind = Mock(side_effect=[OSError, OSError, OSError])
        mock_socket_module.socket = Mock(return_value=mock_socket_object)
        mock_random.randrange = Mock(side_effect=[1, 2, 3] * 3)
        with self.assertRaises(NoFreePortsError):
            find_free_port(start=1, end=4)
