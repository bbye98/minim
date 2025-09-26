from collections import deque
from pathlib import Path
import sys
from typing import Any

from PySide6 import QtCore, QtGui, QtSvg, QtWidgets
import yaml

from .. import __file__, CONFIG_FILE, config

ASSETS_DIR = Path(__file__).parents[2] / "assets"
ICONS_DIR = ASSETS_DIR / "gui/icons"
STYLES_DIR = ASSETS_DIR / "gui/styles"
with open(STYLES_DIR / "colors.yaml", "r", encoding="utf8") as f:
    COLORS = yaml.safe_load(f)
with open(STYLES_DIR / "template.qss", "r", encoding="utf8") as f:
    STYLE_TEMPLATE = f.read()
STYLES = {
    theme: STYLE_TEMPLATE.format(**COLORS[theme]) for theme in {"dark", "light"}
}

if "gui" in config:
    gui_config = config["gui"]
else:
    config["gui"] = gui_config = {"library": {}}
    with CONFIG_FILE.open("w") as f:
        yaml.safe_dump(config, f)


def color_svg(svg_file: str | Path, color: str) -> QtGui.QPixmap:
    """
    Recolor a Scalable Vector Graphics (SVG) image.

    Parameters
    ----------
    svg_file : str or pathlib.Path
        Name of or path to the SVG file.

    color : str
        Color specification.

        **Examples**: :code:`#FF0000`, :code:`rgb(255, 0, 0)`.
    """
    renderer = QtSvg.QSvgRenderer(str(svg_file))
    pixmap = QtGui.QPixmap(28, 28)
    pixmap.fill(QtCore.Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(pixmap)
    renderer.render(painter)
    painter.setCompositionMode(painter.CompositionMode.CompositionMode_SourceIn)
    if not color.startswith("#"):
        color = "#{:02X}{:02X}{:02X}".format(
            *(int(v) for v in color[4:-1].split(", "))
        )
    painter.fillRect(pixmap.rect(), color)
    painter.end()
    return pixmap


def _main() -> None:
    """
    Launch the GUI.
    """
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    if geometry := gui_config.get("geometry"):
        window._is_maximized = is_maximized = gui_config.get(
            "is_maximized", False
        )
        if is_maximized:
            window.setGeometry(
                next(
                    s
                    for s in app.screens()
                    if (
                        (xl := (sg := s.geometry()).x())
                        < geometry[0]
                        < xl + sg.width()
                        and (yl := sg.y()) < geometry[1] < yl + sg.height()
                    )
                ).geometry()
            )
            window._last_geometry = QtCore.QRect(*geometry)
        else:
            window.setGeometry(*geometry)
    else:
        geometry = window.frameGeometry()
        geometry.moveCenter(app.primaryScreen().availableGeometry().center())
        window.move(geometry.topLeft())
        window.resize(1_280, 720)
        gui_config["geometry"] = (
            geometry.x(),
            geometry.y(),
            geometry.width(),
            geometry.height(),
        )
        gui_config["is_maximized"] = False
        with CONFIG_FILE.open("w") as f:
            yaml.safe_dump(config, f)
    window.show()
    sys.exit(app.exec())


class TitleBar(QtWidgets.QWidget):
    """
    Top title bar.
    """

    def __init__(
        self,
        parent: "MainWindow",
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Parameters
        ----------
        parent : minim.gui._core.MainWindow
            Main window.

        *args : tuple[Any, ...], optional
            Additional positional arguments to pass to
            :class:`PySide6.QtWidgets.QWidget`.

        **kwargs : dict[str, Any], optional
            Additional keyword arguments to pass to
            :class:`PySide6.QtWidgets.QWidget`.
        """
        super().__init__(parent=parent, *args, **kwargs)
        self.setFixedHeight(40)

        # State
        self._main_window = self._parent = parent
        self._click_position = None
        self._relative_move_position = None
        self._same_click_count = 0
        self._toggle_theme_icon = str(ICONS_DIR / "dark_light_mode.svg")

        # Layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)

        # Favicon
        favicon = QtWidgets.QLabel()
        favicon.setPixmap(
            QtGui.QPixmap(ASSETS_DIR / "favicon.ico").scaled(
                16,
                16,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
        )
        layout.addWidget(favicon)

        # Title
        layout.addSpacing(4)
        layout.addWidget(QtWidgets.QLabel("Minim"), 1)

        # Light/dark mode toggle button
        self._toggle_theme_button = toggle_theme_button = (
            QtWidgets.QPushButton()
        )
        toggle_theme_button.clicked.connect(parent.toggle_theme)
        toggle_theme_button.setFixedSize(24, 24)
        toggle_theme_button.setIcon(
            QtGui.QIcon(
                color_svg(
                    self._toggle_theme_icon, self._main_window._colors["text"]
                )
            )
        )
        toggle_theme_button.setProperty("role", "theme")
        toggle_theme_button.setToolTip("Toggle light/dark mode")
        layout.addWidget(toggle_theme_button)
        layout.addSpacing(16)

        # Minimize button
        minimize_button = QtWidgets.QPushButton()
        minimize_button.clicked.connect(parent.minimize)
        minimize_button.setFixedSize(16, 16)
        minimize_button.setProperty("role", "minimize")
        minimize_button.setToolTip("Minimize")
        layout.addWidget(minimize_button)

        # Maximize button
        self._maximize_button = maximize_button = QtWidgets.QPushButton()
        maximize_button.clicked.connect(parent.toggle_maximize)
        maximize_button.setFixedSize(16, 16)
        maximize_button.setProperty("role", "maximize")
        maximize_button.setToolTip("Maximize")
        layout.addWidget(maximize_button)

        # Close button
        close_button = QtWidgets.QPushButton()
        close_button.clicked.connect(parent.close)
        close_button.setFixedSize(16, 16)
        close_button.setProperty("role", "close")
        close_button.setToolTip("Close")
        layout.addWidget(close_button)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        # Event: left click
        if event.button() == QtCore.Qt.LeftButton:
            # Store starting mouse position relative to the top left of
            # the window to indicate dragging is in progress
            self._click_position = click_position = (
                event.globalPosition().toPoint()
            )
            self._relative_move_position = (
                click_position - self._parent.frameGeometry().topLeft()
            )

        event.accept()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        parent = self._parent

        # Event: left click and dragging
        if (
            self._relative_move_position
            and event.buttons() & QtCore.Qt.LeftButton
        ):
            cursor = event.globalPosition().toPoint()

            # Restore window first if maximized
            if parent._is_maximized:
                parent.setGeometry(
                    QtCore.QRect(
                        cursor.x()
                        - int(
                            (
                                cursor.x()
                                - (
                                    available_geometry
                                    := parent.screen().availableGeometry()
                                ).x()
                            )
                            * (last_geometry := parent._last_geometry).width()
                            / available_geometry.width()
                        ),
                        0,
                        last_geometry.width(),
                        last_geometry.height(),
                    )
                )
                gui_config["is_maximized"] = parent._is_maximized = False
                self._relative_move_position = (
                    cursor - parent.frameGeometry().topLeft()
                )

            # Move window to follow cursor
            parent.move(cursor - self._relative_move_position)

        event.accept()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        parent = self._parent

        # Event: left click released
        if event.button() == QtCore.Qt.LeftButton:
            release_position = event.globalPosition().toPoint()

            # Event: left click immediately released
            if release_position == self._click_position:
                self._same_click_count += 1
                if self._same_click_count == 2:
                    parent.toggle_maximize()
                    self._same_click_count = 0

            # Event: left click released after draggning
            else:
                self._same_click_count = 0

                # Event: left click released near the top of the screen
                if (
                    self._relative_move_position
                    and not parent._is_maximized
                    and (
                        event.globalPosition().toPoint().y()
                        <= parent.screen().availableGeometry().top() + 10
                    )
                ):
                    # Maximize window
                    parent.toggle_maximize(save_geometry=False)
                    self._same_click_count = 0
                else:
                    # Save current window geometry
                    parent._last_geometry = geometry = parent.geometry()
                    gui_config["geometry"] = (
                        geometry.x(),
                        geometry.y(),
                        geometry.width(),
                        geometry.height(),
                    )
                    with CONFIG_FILE.open("w") as f:
                        yaml.safe_dump(config, f)

        event.accept()
        self._relative_move_position = None

    def toggle_theme(self) -> None:
        """
        Toggle between light and dark modes.
        """
        self._toggle_theme_button.setIcon(
            QtGui.QIcon(
                color_svg(
                    self._toggle_theme_icon, self._main_window._colors["text"]
                )
            )
        )


class NavigationButton(QtWidgets.QPushButton):
    """
    Navigation button.
    """

    def __init__(
        self,
        parent: "NavigationBar",
        svg_file: str | Path,
        name: str,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Parameters
        ----------
        parent : minim.gui._core.NavigationBar
            Nagivation bar.

        svg_file : str or pathlib.Path
            Name of or path to the icon SVG file.

        name : str
            Page name.
        """
        super().__init__(parent=parent, *args, **kwargs)
        self.setCheckable(True)
        self.setFixedSize(128, 64)
        self.setProperty("name", name)
        self.setProperty("role", "navigation")

        # State
        self._main_window = parent._parent
        self._parent = parent
        self._svg_file = str(svg_file)

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0, 8, 0, 8)

        # Icon
        self._icon = icon = QtWidgets.QLabel()
        icon.setAlignment(QtCore.Qt.AlignCenter)
        icon.setPixmap(
            color_svg(self._svg_file, self._main_window._colors["text"])
        )
        layout.addWidget(icon)

        # Text
        text = QtWidgets.QLabel(name.capitalize())
        text.setAlignment(QtCore.Qt.AlignCenter)
        text.setProperty("role", "navigation")
        layout.addWidget(text)

    def toggle_theme(self) -> None:
        """
        Toggle between light and dark modes.
        """
        self._icon.setPixmap(
            color_svg(self._svg_file, self._main_window._colors["text"])
        )


class NavigationBar(QtWidgets.QWidget):
    """
    Bottom navigation bar.
    """

    def __init__(
        self,
        parent: "MainWindow",
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Parameters
        ----------
        parent : minim.gui._core.MainWindow
            Main window.

        *args : tuple[Any, ...], optional
            Additional positional arguments to pass to
            :class:`PySide6.QtWidgets.QWidget`.

        **kwargs : dict[str, Any], optional
            Additional keyword arguments to pass to
            :class:`PySide6.QtWidgets.QWidget`.
        """
        super().__init__(parent=parent, *args, **kwargs)
        self.setFixedHeight(80)

        # State
        self._parent = parent

        # Layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tabs
        self._button_group = button_group = QtWidgets.QButtonGroup()
        button_group.setExclusive(True)
        self._buttons = buttons = [
            NavigationButton(self, ICONS_DIR / f"{icon}.svg", icon)
            for icon in ("library", "search", "settings")
        ]
        for button in buttons:
            button_group.addButton(button)
            layout.addWidget(button)
        buttons[0].setChecked(True)

        # Highlight
        self._highlight = highlight = QtWidgets.QFrame(self)
        highlight.lower()
        highlight.setProperty("role", "navigation")
        QtCore.QTimer.singleShot(0, self.move_highlight)

        # Animation
        self._animation = animation = QtCore.QPropertyAnimation(
            highlight, b"geometry"
        )
        animation.setDuration(200)
        animation.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        button_group.buttonToggled.connect(self.animate_highlight)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        # Keep highlight aligned on resize
        super().resizeEvent(event)
        self.move_highlight()

    def animate_highlight(
        self, button: QtWidgets.QAbstractButton, checked: bool
    ) -> None:
        """
        Animate moving the highlight to the toggled navigation button.

        Parameters
        ----------
        button : PySide6.QtWidgets.QAbstractButton
            Navigation button.

        checked : bool
            Specifies whether the button was toggled.
        """
        if checked:
            animation = self._animation
            animation.setStartValue(self._highlight.geometry())
            animation.setEndValue(button.geometry())
            animation.start()

    def move_highlight(self) -> None:
        """
        Place highlight on the currently toggled button.
        """
        buttons = self._buttons
        self._highlight.setGeometry(
            next((b for b in buttons if b.isChecked()), buttons[0]).geometry()
        )

    def toggle_theme(self) -> None:
        """
        Toggle between light and dark modes.
        """
        for button in self._buttons:
            button.toggle_theme()


class AddressField(QtWidgets.QLineEdit):
    """
    Address field.
    """

    def __init__(self, parent: "AddressBar", address: str = None) -> None:
        """ """
        super().__init__(address, parent)

        # State
        self._parent = parent
        self._main_window = parent._parent._parent
        self.setFixedHeight(32)
        self.returnPressed.connect(parent.load_directory)

        # Completer for recent directories
        self._completer = completer = QtWidgets.QCompleter(
            self._parent._recent_directories, parent=self
        )  # TODO: Apply styling.
        completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.setCompleter(completer)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.selectAll()


class AddressBar(QtWidgets.QWidget):
    """
    Address bar.
    """

    def __init__(
        self,
        parent: "LibraryPage",
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """ """
        super().__init__(parent=parent, *args, **kwargs)

        # State
        self._parent = parent
        self._main_window = parent._parent
        max_n_directoryes = 20
        self._max_directory_index = max_n_directoryes - 1
        self._recent_directories = deque(
            gui_config["library"].get("recent_directories", [str(Path.home())]),
            maxlen=max_n_directoryes,
        )
        self._directory = self._recent_directories[-1]
        self._history = deque([self._directory], maxlen=max_n_directoryes)
        self._directory_index = 0
        self._buttons = {}
        self._favorite_state = "favorite"
        self._icons = {
            icon: str(ICONS_DIR / f"{icon}.svg")
            for icon in [
                "back",
                "forward",
                "refresh",
                "favorite",
                "favorited",
                "bookmarks",
                "home",
            ]
        }

        # Layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)

        # Back button
        self._buttons["back"] = back_button = QtWidgets.QPushButton()
        back_button.setFixedSize(32, 32)
        back_button.setIcon(
            QtGui.QIcon(
                color_svg(
                    self._icons["back"],
                    self._parent._parent._colors["text"],
                )
            )
        )
        back_button.setProperty("name", "back")
        back_button.setProperty("role", "address")
        back_button.setToolTip("Back")
        # back_button.clicked.connect(...)
        layout.addWidget(back_button)

        # Forward button
        self._buttons["forward"] = forward_button = QtWidgets.QPushButton()
        forward_button.setFixedSize(32, 32)
        forward_button.setIcon(
            QtGui.QIcon(
                color_svg(
                    self._icons["forward"],
                    self._parent._parent._colors["text"],
                )
            )
        )
        forward_button.setProperty("name", "forward")
        forward_button.setProperty("role", "address")
        forward_button.setToolTip("Forward")
        # forward_button.clicked.connect(...)
        layout.addWidget(forward_button)

        # Refresh button
        self._buttons["refresh"] = refresh_button = QtWidgets.QPushButton()
        refresh_button.setFixedSize(32, 32)
        refresh_button.setIcon(
            QtGui.QIcon(
                color_svg(
                    self._icons["refresh"],
                    self._parent._parent._colors["text"],
                )
            )
        )
        refresh_button.setProperty("name", "refresh")
        refresh_button.setProperty("role", "address")
        refresh_button.setToolTip("Refresh")
        # refresh_button.clicked.connect(...)
        layout.addWidget(refresh_button)
        layout.addSpacing(12)

        # Address field
        self._directory_field = AddressField(self, self._directory)
        layout.addWidget(self._directory_field)
        layout.addSpacing(12)

        # Favorite button
        self._favorite_button = favorite_button = QtWidgets.QPushButton()
        favorite_button.setFixedSize(32, 32)
        favorite_button.setIcon(
            QtGui.QIcon(
                color_svg(
                    self._icons["favorite"],
                    self._parent._parent._colors["text"],
                )
            )
        )
        favorite_button.setProperty("role", "address")
        favorite_button.setToolTip("Add to bookmarks")
        # favorite_button.clicked.connect(...)
        layout.addWidget(favorite_button)

        # Bookmarks button
        self._buttons["bookmarks"] = bookmarks_button = QtWidgets.QPushButton()
        bookmarks_button.setFixedSize(32, 32)
        bookmarks_button.setIcon(
            QtGui.QIcon(
                color_svg(
                    self._icons["bookmarks"],
                    self._parent._parent._colors["text"],
                )
            )
        )
        bookmarks_button.setProperty("name", "bookmarks")
        bookmarks_button.setProperty("role", "address")
        bookmarks_button.setToolTip("Bookmarks")
        # bookmarks_button.clicked.connect(...)
        layout.addWidget(bookmarks_button)

        # Home button
        self._buttons["home"] = home_button = QtWidgets.QPushButton()
        home_button.setFixedSize(32, 32)
        home_button.setIcon(
            QtGui.QIcon(
                color_svg(
                    self._icons["home"], self._parent._parent._colors["text"]
                )
            )
        )
        home_button.setProperty("name", "home")
        home_button.setProperty("role", "address")
        home_button.setToolTip("Home directory")
        # home_button.clicked.connect(...)
        layout.addWidget(home_button)

    def load_directory(self) -> None:
        """ """
        directory = self._directory_field.text()
        if not directory:
            self._directory_field.setText(self._directory)
        else:
            directory = Path(directory).resolve()
            if not directory.exists():
                ...  # TODO
            elif (
                directory
                != Path(self._history[self._directory_index]).resolve()
            ):
                self._directory = directory = str(directory)
                self._directory_index = min(
                    self._directory_index + 1, self._max_directory_index
                )
                self._history.append(directory)
                if directory in self._recent_directories:
                    self._recent_directories.remove(directory)
                self._recent_directories.append(directory)

                gui_config["library"]["recent_directories"] = list(
                    self._recent_directories
                )
                with CONFIG_FILE.open("w") as f:
                    yaml.safe_dump(config, f)

                self._parent.display_files()

    def toggle_theme(self) -> None:
        """
        Toggle between light and dark modes.
        """
        color = self._main_window._colors["text"]
        for button in self._buttons.values():
            button.setIcon(
                QtGui.QIcon(
                    color_svg(self._icons[button.property("name")], color)
                )
            )
        self._favorite_button.setIcon(
            QtGui.QIcon(color_svg(self._icons[self._favorite_state], color))
        )


class LibraryPage(QtWidgets.QWidget):
    """
    "Library" page.
    """

    def __init__(
        self,
        parent: "MainWindow",
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """ """
        super().__init__(parent, *args, **kwargs)

        # State
        self._parent = parent

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Address bar
        self._directory_bar = AddressBar(self)
        layout.addWidget(self._directory_bar)

        # TEMPORARY
        layout.addStretch()

    def display_files(self) -> None: ...

    def toggle_theme(self) -> None:
        """
        Toggle between light and dark modes.
        """
        self._directory_bar.toggle_theme()


class SearchPage(QtWidgets.QWidget):
    def toggle_theme(self): ...


class SettingsPage(QtWidgets.QWidget):
    def toggle_theme(self): ...


class MainWindow(QtWidgets.QWidget):
    """
    Main window.
    """

    def __init__(
        self, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> None:
        """
        Parameters
        ----------
        *args : tuple[Any, ...], optional
            Additional positional arguments to pass to
            :class:`PySide6.QtWidgets.QWidget`.

        **kwargs : dict[str, Any], optional
            Additional keyword arguments to pass to
            :class:`PySide6.QtWidgets.QWidget`.
        """
        super().__init__(*args, **kwargs)

        # State
        self._is_active = True
        self._is_maximized = False
        self._last_geometry = self.frameGeometry()
        theme = gui_config.get("theme", "dark")
        self._use_dark_mode = theme == "dark"
        self.setStyleSheet(STYLES[theme])

        # Main window
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMinimumSize(1_280, 720)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)

        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Central widget
        self._central_widget = central_widget = QtWidgets.QWidget()
        central_widget.setObjectName("CentralWidget")
        main_layout.addWidget(central_widget)

        # Central layout
        central_layout = QtWidgets.QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        # Title bar
        self._title_bar = title_bar = TitleBar(self)
        central_layout.addWidget(title_bar)

        # Pages
        self._pages = pages = {
            "library": LibraryPage(self),
            "search": SearchPage(),
            "settings": SettingsPage(),
        }
        self._pages_widget = pages_widget = QtWidgets.QStackedWidget()
        for page in pages.values():
            pages_widget.addWidget(page)
        pages_widget.setCurrentWidget(pages["library"])
        central_layout.addWidget(pages_widget)

        # Navigation bar
        self._navigation_bar = navigation_bar = NavigationBar(self)
        central_layout.addWidget(navigation_bar)
        for button in navigation_bar._buttons:
            button.clicked.connect(self.switch_page)

    def minimize(self) -> None:
        """
        Minimize the window.
        """
        if self.isMinimized():
            self.showNormal()
        self.showMinimized()

    def toggle_maximize(self, *, save_geometry: bool = True) -> None:
        """
        Maximize or restore the window.

        Parameters
        ----------
        save_geometry : bool, keyword-only, default: :code:`True`
            Specifies whether to save the current window geometry
            before maximizing. Has no effect when restoring the window.
        """
        self._animation = animation = QtCore.QPropertyAnimation(
            self, b"geometry"
        )
        animation.setDuration(200)
        animation.setEasingCurve(QtCore.QEasingCurve.InOutCirc)

        if self._is_maximized:
            animation.setStartValue(self.geometry())
            animation.setEndValue(self._last_geometry)
        else:
            geometry = self.geometry()
            if save_geometry:
                self._last_geometry = geometry
            animation.setStartValue(geometry)
            animation.setEndValue(self.screen().availableGeometry())
            self._title_bar._maximize_button.setToolTip("Restore")

        animation.start()
        animation.finished.connect(lambda: setattr(self, "_animation", None))
        gui_config["is_maximized"] = self._is_maximized = not self._is_maximized
        with CONFIG_FILE.open("w") as f:
            yaml.safe_dump(config, f)

    def toggle_theme(self) -> None:
        """
        Toggle between light and dark modes.
        """
        self._use_dark_mode = not self._use_dark_mode
        theme = "dark" if self._use_dark_mode else "light"
        self.setStyleSheet(STYLES[theme])
        self._title_bar.toggle_theme()
        self._navigation_bar.toggle_theme()
        for page in self._pages.values():
            page.toggle_theme()

        gui_config["theme"] = theme
        with CONFIG_FILE.open("w") as f:
            yaml.safe_dump(config, f)

    def switch_page(self) -> None:
        """
        Switch pages upon the click of a navigation button.
        """
        if isinstance(sender := self.sender(), NavigationButton) and (
            page := sender.property("name").lower()
        ) in (pages := self._pages):
            self._pages_widget.setCurrentWidget(pages[page])

    @property
    def _colors(self) -> dict[str, str]:
        """
        Color specifications in the current theme.
        """
        return COLORS["dark" if self._use_dark_mode else "light"]

    def _create_library_page(self) -> QtWidgets.QWidget:
        """
        Create the "Library" page.

        Returns
        -------
        library_page : PySide6.QtWidgets.QWidget
            "Library" page.
        """
        library_page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(library_page)
        layout.setContentsMargins(0, 0, 0, 0)
        return library_page

    def _create_search_page(self) -> QtWidgets.QWidget:
        """
        Create the "Search" page.

        Returns
        -------
        search_page : PySide6.QtWidgets.QWidget
            "Search" page.
        """
        search_page = QtWidgets.QWidget()
        return search_page

    def _create_settings_page(self) -> QtWidgets.QWidget:
        """
        Create the "Settings" page.

        Returns
        -------
        settings_page : PySide6.QtWidgets.QWidget
            "Settings" page.
        """
        settings_page = QtWidgets.QWidget()
        return settings_page
