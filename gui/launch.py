from pathlib import Path
import sys

from PySide6 import QtCore, QtGui, QtSvg, QtWidgets
import yaml

import minim

MINIM_DIR = Path(minim.__file__).parents[2]
ICONS_DIR = MINIM_DIR / "gui/icons"
STYLES_DIR = MINIM_DIR / "gui/styles"

with open(STYLES_DIR / "colors.yaml", "r", encoding="utf8") as f:
    COLORS = yaml.safe_load(f)
with open(STYLES_DIR / "template.qss", "r", encoding="utf8") as f:
    STYLE_TEMPLATE = f.read()

STYLES = {
    theme: STYLE_TEMPLATE.format(**COLORS[theme]) for theme in {"dark", "light"}
}


class TitleBar(QtWidgets.QWidget):
    """
    Top title bar.
    """

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        """
        Parameters
        ----------
        parent : QtWidgets.QWidget
            Parent widget (or main window).
        """
        super().__init__(parent)
        self.setFixedHeight(40)

        # State
        self._parent = parent

        # Layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Favicon
        layout.addSpacing(16)
        favicon = QtWidgets.QLabel()
        favicon.setPixmap(
            QtGui.QPixmap(MINIM_DIR / "assets/favicon.ico").scaled(
                16,
                16,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
        )
        layout.addWidget(favicon)

        # Window title
        layout.addSpacing(8)
        self.title_label = QtWidgets.QLabel("Minim")
        layout.addWidget(self.title_label)
        layout.addStretch()

        # Light/dark mode toggle button
        toggle_theme_button = QtWidgets.QPushButton("☯")
        toggle_theme_button.clicked.connect(parent.toggle_theme)
        toggle_theme_button.setFixedSize(24, 24)
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
        self._maximize_button = QtWidgets.QPushButton()
        self._maximize_button.clicked.connect(parent.toggle_maximize)
        self._maximize_button.setFixedSize(16, 16)
        self._maximize_button.setProperty("role", "maximize")
        self._maximize_button.setToolTip("Maximize")
        layout.addWidget(self._maximize_button)

        # Close button
        close_button = QtWidgets.QPushButton()
        close_button.clicked.connect(parent.close)
        close_button.setFixedSize(16, 16)
        close_button.setProperty("role", "close")
        close_button.setToolTip("Close")
        layout.addWidget(close_button)
        layout.addSpacing(12)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """ """
        # Event: left click
        if event.button() == QtCore.Qt.LeftButton:
            # Store starting mouse position relative to the top left of
            # the window to indicate dragging is in progress
            self._parent._relative_drag_position = (
                event.globalPosition().toPoint()
                - self._parent.frameGeometry().topLeft()
            )

        event.accept()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """ """
        parent = self._parent

        # Event: left click and dragging
        if (
            parent._relative_drag_position
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
                parent._is_maximized = False
                parent._relative_drag_position = (
                    cursor - parent.frameGeometry().topLeft()
                )

            # Move window to follow cursor
            parent.move(cursor - parent._relative_drag_position)

        event.accept()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        """ """
        parent = self._parent
        # Event: left click released after dragging and near the top of
        # the screen
        if (
            event.button() == QtCore.Qt.LeftButton
            and parent._relative_drag_position
            and not parent._is_maximized
            and (
                event.globalPosition().toPoint().y()
                <= parent.screen().availableGeometry().top() + 10
            )
        ):
            # Maximize window
            parent.toggle_maximize(save_geometry=False)
        else:
            # Save current window geometry
            parent._last_geometry = parent.geometry()

        event.accept()
        parent._relative_drag_position = None


class NavigationButton(QtWidgets.QPushButton):
    """
    Navigation button.
    """

    def __init__(
        self, parent: QtWidgets.QWidget, icon: str | Path, text: str
    ) -> None:
        """
        Parameters
        ----------
        parent : QtWidgets.QWidget
            Parent widget (or main window).
        """
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(128, 64)
        self.setProperty("role", "navigation")

        # State
        self._icon_svg = str(icon)
        self._parent = parent

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0, 8, 0, 8)

        # Icon
        self._icon_label = QtWidgets.QLabel()
        self._icon_label.setAlignment(QtCore.Qt.AlignCenter)
        self._icon_label.setPixmap(self.icon_pixmap)
        layout.addWidget(self._icon_label)

        # Text
        text_label = QtWidgets.QLabel(text)
        text_label.setAlignment(QtCore.Qt.AlignCenter)
        text_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(text_label)

    @property
    def icon_pixmap(self) -> QtGui.QPixmap:
        """ """
        renderer = QtSvg.QSvgRenderer(self._icon_svg)
        pixmap = QtGui.QPixmap(28, 28)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        renderer.render(painter)
        painter.setCompositionMode(
            painter.CompositionMode.CompositionMode_SourceIn
        )
        painter.fillRect(
            pixmap.rect(),
            "#{:02X}{:02X}{:02X}".format(
                *(
                    int(v)
                    for v in COLORS[
                        "dark"
                        if self._parent._parent._use_dark_mode
                        else "light"
                    ]["base"][4:-1].split(", ")
                )
            ),
        )
        painter.end()
        return pixmap


class NavigationBar(QtWidgets.QWidget):
    """
    Bottom navigation bar.
    """

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        """
        Parameters
        ----------
        parent : QtWidgets.QWidget
            Parent widget (or main window).
        """
        super().__init__(parent)
        self.setFixedHeight(80)

        # State
        self._parent = parent

        # Layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tabs
        self._button_group = QtWidgets.QButtonGroup()
        self._button_group.setExclusive(True)
        self._buttons = [
            NavigationButton(self, ICONS_DIR / f"{icon}.svg", icon.capitalize())
            for icon in ("home", "library", "search", "settings")
        ]
        for button in self._buttons:
            self._button_group.addButton(button)
            layout.addWidget(button)
        self._buttons[0].setChecked(True)

        # Highlight
        self._highlight = QtWidgets.QFrame(self)
        self._highlight.lower()
        self._highlight.setProperty("role", "navigation")
        QtCore.QTimer.singleShot(0, self._update_highlight)

        # Animation
        self._animation = QtCore.QPropertyAnimation(
            self._highlight, b"geometry"
        )
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self._button_group.buttonToggled.connect(self._on_button_toggled)

    def _on_button_toggled(
        self, button: QtWidgets.QAbstractButton, checked: bool
    ) -> None:
        """ """
        if checked:
            self._animation.setStartValue(self._highlight.geometry())
            self._animation.setEndValue(button.geometry())
            self._animation.start()

    def _update_highlight(self) -> None:
        """
        Place highlight on the currently checked button.
        """
        checked_button = next(
            (b for b in self._buttons if b.isChecked()), self._buttons[0]
        )
        self._highlight.setGeometry(checked_button.geometry())

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        """ """
        # Keep highlight aligned on resize
        super().resizeEvent(event)
        self._update_highlight()

    def toggle_theme(self) -> None:
        """ """
        for button in self._buttons:
            button._icon_label.setPixmap(button.icon_pixmap)


class MainWindow(QtWidgets.QWidget):
    """
    Main window.
    """

    def __init__(self) -> None:
        super().__init__()

        # State
        self._is_active = True
        self._is_maximized = False
        self._last_geometry = self.frameGeometry()
        self._relative_drag_position = None
        self._use_dark_mode = True
        self.setStyleSheet(STYLES["dark"])

        # Main window
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMinimumSize(1_280, 800)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)

        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Central widget
        self._central_widget = QtWidgets.QWidget()
        self._central_widget.setObjectName("CentralWidget")
        main_layout.addWidget(self._central_widget)

        # Central layout
        central_layout = QtWidgets.QVBoxLayout(self._central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        # Title bar
        self._title_bar = TitleBar(self)
        central_layout.addWidget(self._title_bar)

        # Content
        self._content = QtWidgets.QWidget()
        # TODO: TBD
        central_layout.addWidget(self._content)

        # Navigation bar
        self._navigation_bar = NavigationBar(self)
        central_layout.addWidget(self._navigation_bar)

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
        self._animation = QtCore.QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QtCore.QEasingCurve.InOutCirc)

        if self._is_maximized:
            self._animation.setStartValue(self.geometry())
            self._animation.setEndValue(self._last_geometry)
        else:
            geometry = self.geometry()
            if save_geometry:
                self._last_geometry = geometry
            self._animation.setStartValue(geometry)
            self._animation.setEndValue(self.screen().availableGeometry())
            self._title_bar._maximize_button.setToolTip("Restore")

        self._animation.start()
        self._animation.finished.connect(
            lambda: setattr(self, "_animation", None)
        )
        self._is_maximized = not self._is_maximized

    def toggle_theme(self) -> None:
        """ """
        self._use_dark_mode = not self._use_dark_mode
        self.setStyleSheet(STYLES["dark" if self._use_dark_mode else "light"])
        self._navigation_bar.toggle_theme()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    screen = app.screens()[-1]
    screen_geometry = screen.availableGeometry()
    window = MainWindow()
    window_geometry = window.frameGeometry()
    window_geometry.moveCenter(screen_geometry.center())
    window.move(window_geometry.topLeft())
    window.resize(1_280, 800)
    window.show()
    sys.exit(app.exec())
