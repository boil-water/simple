import json
import pickle
from PyQt5.QtWidgets import QFileDialog

class AnnotationTool:
    def __init__(self, image_viewer):
        self.image_viewer = image_viewer

    def save_rectangles(self, dicom_file_name):
        if not self.image_viewer.rect_item_list:
            print("没有矩形框可保存")
            return

        rectangles_data = []
        for rect_item, text_item in zip(self.image_viewer.rect_item_list, self.image_viewer.text_item_list):
            rect = rect_item.rect()
            text = text_item.toPlainText()
            rectangles_data.append({
                "x1": rect.topLeft().x(),
                "y1": rect.topLeft().y(),
                "x2": rect.bottomRight().x(),
                "y2": rect.bottomRight().y(),
                "text": text,
                "text_x": text_item.pos().x(),
                "text_y": text_item.pos().y()
            })

        binary_file_name = f"{dicom_file_name}.redcm"
        file_path, _ = QFileDialog.getSaveFileName(self.image_viewer, "Save Rectangle Information", binary_file_name, "REDCM Files (*.redcm)")
        if file_path:
            try:
                with open(file_path, 'wb') as binary_file:
                    pickle.dump(rectangles_data, binary_file)
                print(f"矩形信息和标注已保存到 {file_path}")
            except Exception as e:
                print(f"保存文件失败: {e}")

    def load_rectangles(self, file_path):
        try:
            with open(file_path, 'rb') as binary_file:
                rectangles_data = pickle.load(binary_file)
                return rectangles_data
        except Exception as e:
            print(f"加载文件失败: {e}")
            return None