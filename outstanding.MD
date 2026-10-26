# Outstanding Runners for Local Installation Support

This document lists runners that require additional work to fully support the local installation feature via `install_from_local()`.

## Overview

The local installation feature allows users to install runners from local archive files (.gz, .tar.gz) instead of downloading from the Lutris repository. Most runners have been converted to use the `get_post_install_callback()` pattern, which automatically makes them compatible with local installs.

## Runners Requiring Additional Work

### 1. redream

**Status**: Does not support local installation

**Issue**: The runner requires `install_ui_delegate` to prompt the user for a premium license file during installation.

**Current Implementation**:
```python
def install(self, install_ui_delegate, version=None, callback=None):
    def on_runner_installed(*args):
        license_filename = install_ui_delegate.show_install_file_inquiry(
            question=_("Do you want to select a premium license file?"),
            title=_("Use premium version?"),
            message=_("Use premium version?"),
        )

        if license_filename:
            shutil.copy(license_filename, os.path.join(settings.RUNNER_DIR, "redream"))

    super().install(install_ui_delegate, version=version, callback=on_runner_installed)
```

**Required Work**:
- Add a `get_post_install_callback()` method for the basic installation logic
- For local installs, the user would need to manually place the license file in the runner directory
- Alternatively, add a separate dialog in the GUI to prompt for the license file after local installation
- The post-install callback could check if a license file exists and prompt if missing

**Potential Approaches**:
1. **Manual Documentation**: Document that users should manually copy the license file after local install
2. **GUI Prompt**: Add a dialog in `runner_box.py` to prompt for license file after successful local installation for redream
3. **Conditional Prompt**: Modify `install_from_local()` to accept an optional UI delegate for cases where user interaction is needed

---

### 2. hatari

**Status**: Does not support local installation

**Issue**: The runner requires `install_ui_delegate` to prompt the user for an Atari ST BIOS file during installation.

**Current Implementation**:
```python
def install(self, install_ui_delegate, version=None, callback=None):
    def on_runner_installed(*args):
        bios_path = system.create_folder("~/.hatari/bios")

        bios_filename = install_ui_delegate.show_install_file_inquiry(
            question=_("Do you want to select an Atari ST BIOS file?"),
            title=_("Use BIOS file?"),
            message=_("Select a BIOS file"),
        )

        if bios_filename:
            shutil.copy(bios_filename, bios_path)
            bios_path = os.path.join(bios_path, os.path.basename(bios_filename))
            config = LutrisConfig(runner_slug="hatari")
            config.raw_runner_config.update({"bios_file": bios_path})
            config.save()
        if callback:
            callback()

    super().install(install_ui_delegate, version=version, callback=on_runner_installed)
```

**Required Work**:
- Add a `get_post_install_callback()` method that creates the BIOS directory
- For local installs, the user would need to manually place the BIOS file
- Alternatively, add a separate dialog in the GUI to prompt for the BIOS file after local installation
- The post-install callback should also update the runner configuration

**Potential Approaches**:
1. **Manual Documentation**: Document that users should manually copy the BIOS file after local install
2. **GUI Prompt**: Add a dialog in `runner_box.py` to prompt for BIOS file after successful local installation for hatari
3. **Runner Override**: Have hatari override `install_from_local()` to add its own file selection dialog

---

### 3. atari800

**Status**: Does not support local installation

**Issue**: The runner downloads additional files (BIOS archive) during installation using `install_ui_delegate`.

**Current Implementation**:
```python
def install(self, install_ui_delegate, version=None, callback=None):
    def on_runner_installed(*_args):
        config_path = system.create_folder("~/.atari800")
        bios_archive = os.path.join(config_path, "atari800-bioses.zip")
        install_ui_delegate.download_install_file(self.bios_url, bios_archive)
        if not system.path.exists(bios_archive):
            raise RuntimeError(_("Could not download Atari 800 BIOS archive"))
        extract.extract_archive(bios_archive, config_path)
        os.remove(bios_archive)
        config = LutrisConfig(runner_slug="atari800")
        config.raw_runner_config.update({"bios_path": config_path})
        config.save()
        if callback:
            callback()

    super().install(install_ui_delegate, version, on_runner_installed)
```

**Required Work**:
- The BIOS download is specific to web installations
- For local installs, the user would need to manually download and extract the BIOS archive
- The runner configuration still needs to be updated with the BIOS path
- Could optionally add a feature to download the BIOS separately even after local install

**Potential Approaches**:
1. **Manual Documentation**: Document that users should manually download and extract BIOS files after local install
2. **Separate Download**: Add a method to download BIOS separately (could be called after local install)
3. **Optional Prompt**: Add a GUI option to download BIOS after successful local installation

---

## Non-Installable Runners

These runners intentionally do not support installation via Lutris and will never support local installation:

### 4. steam

**Status**: Intentionally non-installable

**Reason**: Steam for Linux installation is not handled by Lutris. Users must install Steam through their distribution's package manager.

**No action required.**

### 5. flatpak

**Status**: Intentionally non-installable

**Reason**: Flatpak installation is not handled by Lutris. Users must install Flatpak through their distribution's package manager.

**No action required.**

---

## Completed Conversions

The following runners have been successfully converted to use the `get_post_install_callback()` pattern and automatically support local installation:

- ✅ **vice** - Merges lib folders to `~/.vice`
- ✅ **reicast** - Copies mapping files to `~/.reicast/mappings`
- ✅ **o2em** - Creates BIOS directory
- ✅ **libretro** - Clears libretro cores cache
- ✅ **wine** - Cache clearing handled by base Runner class

---

## Recommendations

### Short-term (Documentation)
For now, document that the following runners require manual setup after local installation:
- redream: Manually copy license file
- hatari: Manually copy BIOS file and configure path
- atari800: Manually download and extract BIOS archive

### Medium-term (GUI Enhancements)
Consider adding runner-specific post-installation dialogs in the GUI:
- Detect when a runner that needs additional files is installed locally
- Show a dialog prompting for the required files (license, BIOS, etc.)
- Update runner configuration accordingly

### Long-term (Architecture Enhancement)
Consider extending the `install_from_local()` API to support optional UI interaction:
- Add an optional `ui_delegate` parameter for runners that need user prompts
- Allow runners to override `install_from_local()` with custom logic
- This would enable full feature parity between web and local installations
