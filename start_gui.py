import os
import shutil
import tempfile
from pathlib import Path

import PySide6


def prepare_qt_platform_plugins():
    """
    Help Qt find its platform plugin when PySide6 is installed inside a venv.

    On most machines PySide6 works without this. On some macOS virtual
    environments, Qt sees the plugin folder but does not load "cocoa" from
    inside the venv. Copying the platform plugins to a temporary folder and
    pointing Qt there is harmless on normal installs and fixes that case.
    """
    if os.environ.get("QT_QPA_PLATFORM_PLUGIN_PATH"):
        return

    source = Path(PySide6.__file__).resolve().parent / "Qt" / "plugins" / "platforms"
    if not source.exists():
        return

    temp_root = Path("/tmp") if os.name == "posix" else Path(tempfile.gettempdir())
    target = temp_root / "ap_group_11_qt_platforms"
    target.mkdir(parents=True, exist_ok=True)

    for plugin in source.iterdir():
        if plugin.is_file():
            target_plugin = target / plugin.name
            if target_plugin.exists():
                target_plugin.unlink()
            shutil.copyfile(plugin, target_plugin)

    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(target)


if __name__ == "__main__":
    prepare_qt_platform_plugins()

    from final_project.main import main

    main()
