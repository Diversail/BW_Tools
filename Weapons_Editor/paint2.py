import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QColor, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QRect
import traceback

class BrightnessViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.image_label = QLabel()
        self.image_label.setScaledContents(True)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)

        self.setLayout(layout)

        # Load an image
        self.load_image("messe2d.png")

        # Create an empty image for drawing selection
        self.selection_image = QImage(self.pixmap.size(), QImage.Format_ARGB32)
        self.selection_image.fill(Qt.transparent)

        # Connect the mouse events
        self.image_label.mousePressEvent = self.start_selection
        self.image_label.mouseMoveEvent = self.process_selection
        self.image_label.mouseReleaseEvent = self.apply_brightness_change

        # Variables for selection handling
        self.selection_start = None
        self.selection_end = None

    def load_image(self, path):
        self.pixmap = QPixmap(path)
        self.image_label.setPixmap(self.pixmap)

    def start_selection(self, event):
        self.selection_start = event.pos()
        self.selection_end = event.pos()

    def process_selection(self, event):
        if self.selection_start is not None:
            self.selection_end = event.pos()
            self.update_selection_image()

    def update_selection_image(self):
        self.selection_image.fill(Qt.transparent)
        painter = QPainter(self.selection_image)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        rect = QRect(self.selection_start, self.selection_end).normalized()
        painter.drawRect(rect)
        painter.end()
        self.image_label.setPixmap(self.pixmap.copy())
        painter = QPainter(self.image_label.pixmap())
        painter.drawImage(0, 0, self.selection_image)

    def apply_brightness_change(self, event):
        try:
            if self.selection_start is not None and self.selection_end is not None:
                brightness_increase_percentage = 1.1  # 10% increase
                selection_rect = QRect(self.selection_start, self.selection_end).normalized()
                selected_area = self.pixmap.copy(selection_rect).toImage()  # Convert to QImage
                for y in range(selection_rect.height()):
                    print(y)
                    for x in range(selection_rect.width()):
                        pixel_color = QColor(selected_area.pixel(x, y))  # Get pixel color
                        brightness = (pixel_color.lightness()+20) * brightness_increase_percentage
                        brightness = min(brightness, 255)
                        new_color = QColor.fromHsl(pixel_color.hslHue(), pixel_color.hslSaturation(), int(brightness))
                        selected_area.setPixelColor(x, y, new_color)  # Set new pixel color
                painter = QPainter(self.pixmap)
                painter.drawImage(selection_rect.topLeft(), selected_area)  # Draw modified area onto pixmap
                painter.end()
                self.image_label.setPixmap(self.pixmap)
                self.selection_start = None
                self.selection_end = None
        except:
            traceback.print_exc()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = BrightnessViewer()
    viewer.show()
    sys.exit(app.exec_())
