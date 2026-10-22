import unittest
from unittest.mock import MagicMock, patch

from lutris.exceptions import GameConfigError, MissingGameExecutableError
from lutris.runners.vice import vice
from lutris.util.test_config import setup_test_environment

setup_test_environment()


class TestViceRunner(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.runner = vice()
        self.runner.get_executable = lambda machine="c64": "/path/to/vice/bin/x64"
        self.runner.get_env = lambda: {
            "PATH": "/valid/path/to",
            "LD_LIBRARY_PATH": "/usr/lib",
        }

    @patch("lutris.util.system.path_exists")
    def test_play_no_rom_provided(self, mock_path_exists):
        mock_config = MagicMock()
        mock_config.game_config = {}
        mock_config.runner_config = {}
        self.runner.config = mock_config
        with self.assertRaises(GameConfigError):
            self.runner.play()

    @patch("lutris.util.system.path_exists")
    def test_play_rom_does_not_exist(self, mock_path_exists):
        rom_path = "/invalid/path/to/rom.d64"
        mock_path_exists.return_value = False
        mock_config = MagicMock()
        mock_config.game_config = {"main_file": rom_path}
        mock_config.runner_config = {}
        self.runner.config = mock_config
        with self.assertRaises(MissingGameExecutableError) as cm:
            self.runner.play()
        self.assertEqual(cm.exception.filename, rom_path)

    @patch("lutris.util.system.path_exists")
    def test_play_basic(self, mock_path_exists):
        rom_path = "/valid/path/to/game.d64"
        mock_path_exists.return_value = True
        mock_config = MagicMock()
        mock_config.game_config = {"main_file": rom_path}
        mock_config.runner_config = {"platform": "c64"}
        self.runner.config = mock_config
        expected = {
            "command": [
                "/path/to/vice/bin/x64",
                "-chdir",
                "/valid/path/to",
                "-directory",
                "/path/to/vice/share/vice",
                rom_path,
            ],
            "env": {"LD_LIBRARY_PATH": "/path/to/vice/lib64:/usr/lib", "PATH": "/valid/path/to"},
        }
        self.assertEqual(self.runner.play(), expected)

    @patch("lutris.util.system.path_exists")
    def test_play_fullscreen(self, mock_path_exists):
        rom_path = "/valid/path/to/game.d64"
        mock_path_exists.return_value = True
        mock_config = MagicMock()
        mock_config.game_config = {"main_file": rom_path}
        mock_config.runner_config = {"platform": "c64", "fullscreen": True}
        self.runner.config = mock_config
        expected = {
            "command": [
                "/path/to/vice/bin/x64",
                "-chdir",
                "/valid/path/to",
                "-directory",
                "/path/to/vice/share/vice",
                "-VICIIfull",
                rom_path,
            ],
            "env": {"LD_LIBRARY_PATH": "/path/to/vice/lib64:/usr/lib", "PATH": "/valid/path/to"},
        }
        self.assertEqual(self.runner.play(), expected)

    @patch("lutris.util.system.path_exists")
    def test_play_no_double_scaling(self, mock_path_exists):
        rom_path = "/valid/path/to/game.d64"
        mock_path_exists.return_value = True
        mock_config = MagicMock()
        mock_config.game_config = {"main_file": rom_path}
        mock_config.runner_config = {"platform": "c64", "double": False}
        self.runner.config = mock_config
        expected = {
            "command": [
                "/path/to/vice/bin/x64",
                "-chdir",
                "/valid/path/to",
                "-directory",
                "/path/to/vice/share/vice",
                rom_path,
            ],
            "env": {"LD_LIBRARY_PATH": "/path/to/vice/lib64:/usr/lib", "PATH": "/valid/path/to"},
        }
        self.assertEqual(self.runner.play(), expected)

    @patch("lutris.util.system.path_exists")
    def test_play_software_renderer(self, mock_path_exists):
        rom_path = "/valid/path/to/game.d64"
        mock_config = MagicMock()
        mock_config.game_config = {"main_file": rom_path}
        mock_config.runner_config = {
            "platform": "c64",
            "renderer": "software",
        }
        self.runner.config = mock_config
        expected = {
            "command": [
                "/path/to/vice/bin/x64",
                "-chdir",
                "/valid/path/to",
                "-directory",
                "/path/to/vice/share/vice",
                "-sdl2backend",
                "software",
                rom_path,
            ],
            "env": {"LD_LIBRARY_PATH": "/path/to/vice/lib64:/usr/lib", "PATH": "/valid/path/to"},
        }
        self.assertEqual(self.runner.play(), expected)

    @patch("lutris.util.system.path_exists")
    def test_play_no_aspect_ratio(self, mock_path_exists):
        rom_path = "/valid/path/to/game.d64"
        mock_path_exists.return_value = True
        mock_config = MagicMock()
        mock_config.game_config = {"main_file": rom_path}
        mock_config.runner_config = {
            "platform": "c64",
            "aspect_ratio": False,
        }
        self.runner.config = mock_config
        expected = {
            "command": [
                "/path/to/vice/bin/x64",
                "-chdir",
                "/valid/path/to",
                "-directory",
                "/path/to/vice/share/vice",
                "-sdlaspectmode",
                "0",
                rom_path,
            ],
            "env": {"LD_LIBRARY_PATH": "/path/to/vice/lib64:/usr/lib", "PATH": "/valid/path/to"},
        }
        self.assertEqual(self.runner.play(), expected)

    @patch("lutris.util.system.path_exists")
    def test_play_drivesound(self, mock_path_exists):
        rom_path = "/valid/path/to/game.d64"
        mock_path_exists.return_value = True
        mock_config = MagicMock()
        mock_config.game_config = {"main_file": rom_path}
        mock_config.runner_config = {"platform": "c64", "drivesound": True}
        self.runner.config = mock_config
        expected = {
            "command": [
                "/path/to/vice/bin/x64",
                "-chdir",
                "/valid/path/to",
                "-directory",
                "/path/to/vice/share/vice",
                "-drivesound",
                rom_path,
            ],
            "env": {"LD_LIBRARY_PATH": "/path/to/vice/lib64:/usr/lib", "PATH": "/valid/path/to"},
        }
        self.assertEqual(self.runner.play(), expected)

    @patch("lutris.util.system.path_exists")
    def test_play_joystick(self, mock_path_exists):
        rom_path = "/valid/path/to/game.d64"
        mock_path_exists.return_value = True
        mock_config = MagicMock()
        mock_config.game_config = {"main_file": rom_path}
        mock_config.runner_config = {"platform": "c64", "joy": True}
        self.runner.config = mock_config
        expected = {
            "command": [
                "/path/to/vice/bin/x64",
                "-chdir",
                "/valid/path/to",
                "-directory",
                "/path/to/vice/share/vice",
                "-joydev1",
                "4",
                "-joydev2",
                "4",
                rom_path,
            ],
            "env": {"LD_LIBRARY_PATH": "/path/to/vice/lib64:/usr/lib", "PATH": "/valid/path/to"},
        }
        self.assertEqual(self.runner.play(), expected)

    @patch("lutris.util.system.path_exists")
    def test_play_crt_file(self, mock_path_exists):
        rom_path = "/valid/path/to/game.crt"
        mock_path_exists.return_value = True
        mock_config = MagicMock()
        mock_config.game_config = {"main_file": rom_path}
        mock_config.runner_config = {"platform": "c64"}
        self.runner.config = mock_config
        expected = {
            "command": [
                "/path/to/vice/bin/x64",
                "-chdir",
                "/valid/path/to",
                "-directory",
                "/path/to/vice/share/vice",
                "-cartcrt",
                rom_path,
            ],
            "env": {"LD_LIBRARY_PATH": "/path/to/vice/lib64:/usr/lib", "PATH": "/valid/path/to"},
        }
        self.assertEqual(self.runner.play(), expected)

    @patch("lutris.util.system.path_exists")
    def test_play_vic20_machine(self, mock_path_exists):
        mock_path_exists.return_value = True
        rom_path = "/valid/path/to/game.prg"
        mock_config = MagicMock()
        mock_config.game_config = {"main_file": rom_path}
        mock_config.runner_config = {"platform": "vic20"}
        self.runner.config = mock_config
        self.runner.get_executable = lambda machine="vic20": "/path/to/vice/bin/xvic"
        expected = {
            "command": [
                "/path/to/vice/bin/xvic",
                "-chdir",
                "/valid/path/to",
                "-directory",
                "/path/to/vice/share/vice",
                rom_path,
            ],
            "env": {"LD_LIBRARY_PATH": "/path/to/vice/lib64:/usr/lib", "PATH": "/valid/path/to"},
        }
        self.assertEqual(self.runner.play(), expected)

    @patch("lutris.util.system.path_exists")
    def test_play_vic20_machine_memory_no_expnsion(self, mock_path_exists):
        mock_path_exists.return_value = True
        rom_path = "/valid/path/to/game.prg"
        mock_config = MagicMock()
        mock_config.game_config = {"main_file": rom_path}
        mock_config.runner_config = {"platform": "vic20", "ramexpansion": "none"}
        self.runner.config = mock_config
        self.runner.get_executable = lambda machine="vic20": "/path/to/vice/bin/xvic"
        expected = {
            "command": [
                "/path/to/vice/bin/xvic",
                "-chdir",
                "/valid/path/to",
                "-directory",
                "/path/to/vice/share/vice",
                rom_path,
            ],
            "env": {"LD_LIBRARY_PATH": "/path/to/vice/lib64:/usr/lib", "PATH": "/valid/path/to"},
        }
        self.assertEqual(self.runner.play(), expected)

    @patch("lutris.util.system.path_exists")
    def test_play_vic20_machine_memory_3k_expnsion(self, mock_path_exists):
        mock_path_exists.return_value = True
        rom_path = "/valid/path/to/game.prg"
        mock_config = MagicMock()
        mock_config.game_config = {"main_file": rom_path}
        mock_config.runner_config = {"platform": "vic20", "ramexpansion": "3k"}
        self.runner.config = mock_config
        self.runner.get_executable = lambda machine="vic20": "/path/to/vice/bin/xvic"
        expected = {
            "command": [
                "/path/to/vice/bin/xvic",
                "-chdir",
                "/valid/path/to",
                "-directory",
                "/path/to/vice/share/vice",
                "-memory",
                "3k",
                rom_path,
            ],
            "env": {"LD_LIBRARY_PATH": "/path/to/vice/lib64:/usr/lib", "PATH": "/valid/path/to"},
        }
        self.assertEqual(self.runner.play(), expected)

    @patch("lutris.util.system.path_exists")
    def test_play_all_options(self, mock_path_exists):
        rom_path = "/valid/path/to/game.d64"
        mock_path_exists.return_value = True
        mock_config = MagicMock()
        mock_config.game_config = {"main_file": rom_path}
        self.runner.get_executable = lambda machine="vic20": "/path/to/vice/bin/xvic"
        mock_config.runner_config = {
            "machine": "vic20",
            "fullscreen": True,
            "double": True,
            "renderer": "opengl",
            "aspect_ratio": True,
            "drivesound": True,
            "joy": True,
        }
        self.runner.config = mock_config
        expected = {
            "command": [
                "/path/to/vice/bin/xvic",
                "-chdir",
                "/valid/path/to",
                "-directory",
                "/path/to/vice/share/vice",
                "-VICfull",
                "-VICdsize",
                "-sdl2backend",
                "opengl",
                "-drivesound",
                "-joydev1",
                "4",
                rom_path,
            ],
            "env": {"LD_LIBRARY_PATH": "/path/to/vice/lib64:/usr/lib", "PATH": "/valid/path/to"},
        }
        self.assertEqual(self.runner.play(), expected)

    def test_get_roms_location(self):
        """Test that get_roms_location returns the correct path."""
        expected = "/path/to/vice/share/vice"
        self.assertEqual(self.runner.get_roms_location(), expected)

    def test_get_roms_path_default_machine(self):
        """Test that get_roms_path returns the correct path for default machine (c64)."""
        expected = "/path/to/vice/share/vice/C64"
        self.assertEqual(self.runner.get_roms_path(), expected)

    def test_get_roms_path_c64(self):
        """Test that get_roms_path returns the correct path for c64 machine."""
        expected = "/path/to/vice/share/vice/C64"
        self.assertEqual(self.runner.get_roms_path("c64"), expected)

    def test_get_roms_path_c128(self):
        """Test that get_roms_path returns the correct path for c128 machine."""
        expected = "/path/to/vice/share/vice/C128"
        self.assertEqual(self.runner.get_roms_path("c128"), expected)

    def test_get_roms_path_vic20(self):
        """Test that get_roms_path returns the correct path for vic20 machine."""
        expected = "/path/to/vice/share/vice/VIC20"
        self.assertEqual(self.runner.get_roms_path("vic20"), expected)

    def test_get_roms_path_pet(self):
        """Test that get_roms_path returns the correct path for pet machine."""
        expected = "/path/to/vice/share/vice/PET"
        self.assertEqual(self.runner.get_roms_path("pet"), expected)

    def test_get_roms_path_plus4(self):
        """Test that get_roms_path returns the correct path for plus4 machine."""
        expected = "/path/to/vice/share/vice/PLUS4"
        self.assertEqual(self.runner.get_roms_path("plus4"), expected)

    def test_get_roms_path_cbmii(self):
        """Test that get_roms_path returns the correct path for cbmii machine."""
        expected = "/path/to/vice/share/vice/CBM-II"
        self.assertEqual(self.runner.get_roms_path("cbmii"), expected)
