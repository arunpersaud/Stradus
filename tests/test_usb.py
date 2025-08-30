"""Tests for usb module."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from vortran.usb import (
    parse_bus_and_address,
    _find_libusb_in_site_packages,
    get_usb_backend,
)


class TestParseBusAndAddress:
    """Tests for parse_bus_and_address function."""

    def test_parse_valid_usb_string(self):
        """Test parsing valid USB device string."""
        text = "Bus 002 Address 003, Spec 2.00"
        bus, address = parse_bus_and_address(text)
        assert bus == 2
        assert address == 3

    def test_parse_different_numbers(self):
        """Test parsing with different bus and address numbers."""
        text = "Bus 001 Address 015, Spec 1.10"
        bus, address = parse_bus_and_address(text)
        assert bus == 1
        assert address == 15

    def test_parse_missing_bus(self):
        """Test parsing string missing bus information."""
        text = "Address 003, Spec 2.00"
        bus, address = parse_bus_and_address(text)
        assert bus is None
        assert address == 3

    def test_parse_missing_address(self):
        """Test parsing string missing address information."""
        text = "Bus 002, Spec 2.00"
        bus, address = parse_bus_and_address(text)
        # The regex for bus actually matches 'Bus 002,' so it fails to parse
        assert bus is None
        assert address is None

    def test_parse_missing_both(self):
        """Test parsing string missing both bus and address."""
        text = "Spec 2.00"
        bus, address = parse_bus_and_address(text)
        assert bus is None
        assert address is None

    def test_parse_invalid_bus_number(self):
        """Test parsing with non-numeric bus."""
        text = "Bus ABC Address 003, Spec 2.00"
        bus, address = parse_bus_and_address(text)
        assert bus is None
        assert address == 3

    def test_parse_invalid_address_number(self):
        """Test parsing with non-numeric address."""
        text = "Bus 002 Address XYZ, Spec 2.00"
        bus, address = parse_bus_and_address(text)
        assert bus == 2
        assert address is None

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        text = ""
        bus, address = parse_bus_and_address(text)
        assert bus is None
        assert address is None


class TestFindLibusbInSitePackages:
    """Tests for _find_libusb_in_site_packages function."""

    @patch("vortran.usb.platform.system")
    @patch("vortran.usb.site.getsitepackages")
    @patch("vortran.usb.site.getusersitepackages")
    @patch("vortran.usb.platform.architecture")
    def test_find_libusb_windows_64bit(
        self, mock_arch, mock_user_site, mock_site_packages, mock_platform
    ):
        """Test finding libusb on Windows 64-bit."""
        mock_platform.return_value = "Windows"
        mock_arch.return_value = ("64bit", "WindowsPE")
        mock_site_packages.return_value = ["/fake/site-packages"]
        mock_user_site.return_value = "/fake/user-site"

        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            result = _find_libusb_in_site_packages()

            expected_path = Path(
                "/fake/site-packages/libusb/_platform/_windows/x64/libusb-1.0.dll"
            )
            assert result == expected_path

    @patch("vortran.usb.platform.system")
    @patch("vortran.usb.site.getsitepackages")
    @patch("vortran.usb.platform.architecture")
    def test_find_libusb_windows_32bit(
        self, mock_arch, mock_site_packages, mock_platform
    ):
        """Test finding libusb on Windows 32-bit."""
        mock_platform.return_value = "Windows"
        mock_arch.return_value = ("32bit", "WindowsPE")
        mock_site_packages.return_value = ["/fake/site-packages"]

        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            result = _find_libusb_in_site_packages()

            expected_path = Path(
                "/fake/site-packages/libusb/_platform/_windows/x86/libusb-1.0.dll"
            )
            assert result == expected_path

    @patch("vortran.usb.platform.system")
    def test_find_libusb_non_windows(self, mock_platform):
        """Test finding libusb on non-Windows platform."""
        mock_platform.return_value = "Linux"
        result = _find_libusb_in_site_packages()
        assert result is None

    @patch("vortran.usb.platform.system")
    @patch("vortran.usb.site.getsitepackages")
    @patch("vortran.usb.platform.architecture")
    def test_find_libusb_not_found(self, mock_arch, mock_site_packages, mock_platform):
        """Test when libusb is not found in site-packages."""
        mock_platform.return_value = "Windows"
        mock_arch.return_value = ("64bit", "WindowsPE")
        mock_site_packages.return_value = ["/fake/site-packages"]

        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = False
            result = _find_libusb_in_site_packages()
            assert result is None

    @patch("vortran.usb.platform.system")
    @patch("vortran.usb.site.getsitepackages")
    @patch("vortran.usb.platform.architecture")
    def test_find_libusb_unsupported_architecture(
        self, mock_arch, mock_site_packages, mock_platform
    ):
        """Test with unsupported architecture."""
        mock_platform.return_value = "Windows"
        mock_arch.return_value = ("ARM", "WindowsPE")
        mock_site_packages.return_value = ["/fake/site-packages"]

        result = _find_libusb_in_site_packages()
        assert result is None


class TestGetUsbBackend:
    """Tests for get_usb_backend function."""

    @patch("vortran.usb.platform.system")
    def test_get_usb_backend_non_windows(self, mock_platform):
        """Test get_usb_backend on non-Windows platform."""
        mock_platform.return_value = "Linux"
        result = get_usb_backend()
        assert result is None

    @patch("vortran.usb.platform.system")
    @patch("vortran.usb.os.getenv")
    def test_get_usb_backend_custom_path_exists(self, mock_getenv, mock_platform):
        """Test get_usb_backend with valid custom path."""
        mock_platform.return_value = "Windows"
        mock_getenv.return_value = "/custom/path/libusb-1.0.dll"

        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            with patch("vortran.usb.usb.backend.libusb1.get_backend") as mock_backend:
                mock_backend.return_value = MagicMock()
                result = get_usb_backend()

                assert result is not None
                mock_backend.assert_called_once()

    @patch("vortran.usb.platform.system")
    @patch("vortran.usb.os.getenv")
    def test_get_usb_backend_custom_path_not_exists(self, mock_getenv, mock_platform):
        """Test get_usb_backend with invalid custom path."""
        mock_platform.return_value = "Windows"
        mock_getenv.return_value = "/invalid/path/libusb-1.0.dll"

        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = False
            with pytest.raises(FileNotFoundError) as exc_info:
                get_usb_backend()

            assert "Custom libusb library not found" in str(exc_info.value)

    @patch("vortran.usb.platform.system")
    @patch("vortran.usb.os.getenv")
    @patch("vortran.usb._find_libusb_in_site_packages")
    def test_get_usb_backend_site_packages_found(
        self, mock_find_site, mock_getenv, mock_platform
    ):
        """Test get_usb_backend finding libusb in site-packages."""
        mock_platform.return_value = "Windows"
        mock_getenv.return_value = None  # No custom path
        mock_find_site.return_value = Path("/site/packages/libusb-1.0.dll")

        with patch("vortran.usb.usb.backend.libusb1.get_backend") as mock_backend:
            mock_backend.return_value = MagicMock()
            result = get_usb_backend()

            assert result is not None
            mock_backend.assert_called_once()

    @patch("vortran.usb.platform.system")
    @patch("vortran.usb.os.getenv")
    @patch("vortran.usb._find_libusb_in_site_packages")
    @patch("vortran.usb.platform.architecture")
    def test_get_usb_backend_default_path_exists(
        self, mock_arch, mock_find_site, mock_getenv, mock_platform
    ):
        """Test get_usb_backend using default path."""
        mock_platform.return_value = "Windows"
        mock_getenv.return_value = None  # No custom path
        mock_find_site.return_value = None  # Not in site-packages
        mock_arch.return_value = ("64bit", "WindowsPE")

        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            with patch("vortran.usb.usb.backend.libusb1.get_backend") as mock_backend:
                mock_backend.return_value = MagicMock()
                result = get_usb_backend()

                assert result is not None
                mock_backend.assert_called_once()

    @patch("vortran.usb.platform.system")
    @patch("vortran.usb.os.getenv")
    @patch("vortran.usb._find_libusb_in_site_packages")
    @patch("vortran.usb.platform.architecture")
    def test_get_usb_backend_no_library_found(
        self, mock_arch, mock_find_site, mock_getenv, mock_platform
    ):
        """Test get_usb_backend when no library is found."""
        mock_platform.return_value = "Windows"
        mock_getenv.return_value = None  # No custom path
        mock_find_site.return_value = None  # Not in site-packages
        mock_arch.return_value = ("64bit", "WindowsPE")

        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = False
            with pytest.raises(FileNotFoundError) as exc_info:
                get_usb_backend()

            error_msg = str(exc_info.value)
            assert "libusb library not found" in error_msg
            assert "Environment variable: VORTRAN_LIBUSB_PATH" in error_msg
            assert "Site-packages: libusb package" in error_msg

    @patch("vortran.usb.platform.system")
    @patch("vortran.usb.os.getenv")
    @patch("vortran.usb._find_libusb_in_site_packages")
    @patch("vortran.usb.platform.architecture")
    def test_get_usb_backend_unsupported_architecture(
        self, mock_arch, mock_find_site, mock_getenv, mock_platform
    ):
        """Test get_usb_backend with unsupported architecture."""
        mock_platform.return_value = "Windows"
        mock_getenv.return_value = None  # No custom path
        mock_find_site.return_value = None  # Not in site-packages
        mock_arch.return_value = ("ARM", "WindowsPE")

        with pytest.raises(Exception) as exc_info:
            get_usb_backend()

        assert "Invalid platform" in str(exc_info.value)
