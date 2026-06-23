import os
import shutil
import sys
import socket
import tempfile

from pathlib import Path

import PySide6


def _prepare_qt_platform_plugins():
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


_prepare_qt_platform_plugins()

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

try:
    from .viewmodels.mainViewModel import MainViewModel
    from .views.mainView import MainView
except ImportError:
    from viewmodels.mainViewModel import MainViewModel
    from views.mainView import MainView


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _is_port_available(host="127.0.0.1", port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def _start_embedded_tcp_server(host="127.0.0.1", port=12345):
    if not _is_port_available(host, port):
        return None

    try:
        from TCP_Server.main import EMGTCPServer
    except ImportError as error:
        print(f"Could not import TCP server: {error}")
        return None

    try:
        server = EMGTCPServer(host=host, port=port)
        server.start()
        return server
    except OSError as error:
        print(f"Could not start embedded TCP server: {error}")
        return None


def main():
    qt_plugins = Path(PySide6.__file__).resolve().parent / "Qt" / "plugins"
    QCoreApplication.addLibraryPath(str(qt_plugins))

    embedded_server = _start_embedded_tcp_server()

    app = QApplication(sys.argv)

    view_model = MainViewModel()
    view = MainView(view_model)
    view.showMaximized()

    try:
        exit_code = app.exec()
    finally:
        if embedded_server is not None:
            embedded_server.stop()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
