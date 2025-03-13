from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtCore import Qt, QRectF, QPoint
from PIL import Image
from PyQt5.QtWidgets import QGraphicsTextItem, QInputDialog

class ImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.rect_item_list = []
        self.rect_start = QPoint()
        self.rect_end = QPoint()
        self.rect_item = None
        self.text_item_list = []

    def update_image(self, image_data, cols, rows):
        try:
            self.image = Image.new("L", (cols, rows))
            self.image.putdata(image_data)
            image_data_bytes = self.image.tobytes()
            q_image = QImage(image_data_bytes, cols, rows, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.setFixedSize(cols, rows)
        except Exception as e:
            print(f"图像更新失败: {e}")

    def load_rectangles(self, rectangles_data):
        for data in rectangles_data:
            rect_item = QGraphicsRectItem(QRectF(data["x1"], data["y1"], data["x2"] - data["x1"], data["y2"] - data["y1"]))
            rect_item.setPen(QColor(255, 0, 0))
            rect_item.setBrush(QColor(0, 0, 0, 0))
            rect_item.setZValue(1)
            self.scene.addItem(rect_item)
            self.rect_item_list.append(rect_item)

            text_item = QGraphicsTextItem(data["text"])
            text_item.setPos(data["text_x"], data["text_y"])
            text_item.setDefaultTextColor(QColor(255, 0, 0))
            self.scene.addItem(text_item)
            self.text_item_list.append(text_item)