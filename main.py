from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, QFileDialog
from dicom_viewer.dicom_reader import DicomData
from dicom_viewer.image_viewer import ImageViewer
from dicom_viewer.annotation_tool import AnnotationTool
from dicom_viewer.vtk_viewer import VTKViewer  # 导入 VTKViewer


class DicomViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.data = DicomData()
        self.image_viewer = ImageViewer()
        self.annotation_tool = AnnotationTool(self.image_viewer)
        self.dicom_file_path = ""
        self.dicom_file_name = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("DICOM Viewer")

        # 主布局：水平布局，左侧为 2D 图像显示区域，右侧为 VTK 显示区域
        self.main_layout = QHBoxLayout()

        # 左侧布局：2D 图像显示区域和操作按钮
        self.left_layout = QVBoxLayout()

        # 添加顶部按钮（打开文件、保存标注、删除标注、VTK 体绘制）
        self.button_layout = QHBoxLayout()
        self.file_button = QPushButton("Open File")
        self.file_button.clicked.connect(self.open_dicom_file)
        self.button_layout.addWidget(self.file_button)

        self.save_button = QPushButton("Save Rectangle Information")
        self.save_button.clicked.connect(self.save_rectangles)
        self.button_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("Return")
        self.delete_button.clicked.connect(self.delete_last_rectangle)
        self.button_layout.addWidget(self.delete_button)

        # 添加 VTK 按钮
        self.vtk_button = QPushButton("Open DICOM Folder for 3D View")
        self.vtk_button.clicked.connect(self.open_dicom_folder_for_vtk)
        self.button_layout.addWidget(self.vtk_button)

        self.left_layout.addLayout(self.button_layout)

        # 添加窗宽窗位调整区域
        self.window_layout = QVBoxLayout()
        self.window_center_slider = QSlider(Qt.Horizontal)
        self.window_center_slider.setRange(-1000, 1000)
        self.window_center_slider.setValue(self.data.window_center)
        self.window_center_slider.valueChanged.connect(self.update_window_center)
        self.window_center_label = QLabel(f"Window Center: {self.data.window_center}")
        self.window_layout.addWidget(self.window_center_label)
        self.window_layout.addWidget(self.window_center_slider)

        self.window_width_slider = QSlider(Qt.Horizontal)
        self.window_width_slider.setRange(0, 3000)
        self.window_width_slider.setValue(self.data.window_width)
        self.window_width_slider.valueChanged.connect(self.update_window_width)
        self.window_width_label = QLabel(f"Window Width: {self.data.window_width}")
        self.window_layout.addWidget(self.window_width_label)
        self.window_layout.addWidget(self.window_width_slider)

        self.left_layout.addLayout(self.window_layout)

        # 添加 2D 图像显示区域
        self.left_layout.addWidget(self.image_viewer)

        # 添加元数据显示区域
        self.metadata_label = QLabel(self)
        self.left_layout.addWidget(self.metadata_label)

        # 将左侧布局添加到主布局
        self.main_layout.addLayout(self.left_layout)

        # 右侧布局：VTK 显示区域
        self.right_layout = QVBoxLayout()

        # 创建 VTKViewer 实例
        self.vtk_viewer = VTKViewer()

        # 将 VTKViewer 添加到右侧布局
        self.right_layout.addWidget(self.vtk_viewer)

        # 将右侧布局添加到主布局
        self.main_layout.addLayout(self.right_layout)

        # 设置主布局
        self.setLayout(self.main_layout)

    def open_dicom_file(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open DICOM File", "", "DICOM Files (*.dcm)")
            if not file_path:
                print("未选择文件。")
                return

            print(f"正在加载文件: {file_path}")
            self.data.parse_file(file_path)

            self.dicom_file_path = file_path
            self.dicom_file_name = file_path.split("/")[-1].split(".")[0]

            print("文件解析完成，正在更新图像和元数据...")
            self.update_image()
            self.update_metadata()

            print("更新完成！")
        except Exception as e:
            print(f"打开 DICOM 文件失败: {e}")

    def update_image(self):
        try:
            pixels = self.data.get_image_data()
            print(f"像素数据长度: {len(pixels)}")
            print(f"图像大小: {self.data.cols}x{self.data.rows}")

            if len(pixels) == 0:
                print("没有有效的像素数据")
                return

            self.image_viewer.update_image(pixels, self.data.cols, self.data.rows)
        except Exception as e:
            print(f"图像更新失败: {e}")

    def update_metadata(self):
        try:
            metadata = self.data.get_metadata()
            print("提取到的元数据:")
            for key, value in metadata.items():
                print(f"{key}: {value}")

            metadata_text = "\n".join([f"{key}: {value}" for key, value in metadata.items()])
            self.metadata_label.setText(metadata_text)
        except Exception as e:
            print(f"元数据更新失败: {e}")

    def update_window_center(self):
        self.data.window_center = self.window_center_slider.value()
        self.window_center_label.setText(f"Window Center: {self.data.window_center}")
        self.update_image()

    def update_window_width(self):
        self.data.window_width = self.window_width_slider.value()
        self.window_width_label.setText(f"Window Width: {self.data.window_width}")
        self.update_image()

    def delete_last_rectangle(self):
        self.image_viewer.delete_last_rectangle()

    def save_rectangles(self):
        self.annotation_tool.save_rectangles(self.dicom_file_name)

    def open_dicom_folder_for_vtk(self):
        """打开 DICOM 文件夹并进行体绘制"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select DICOM Folder")
        if folder_path:
            try:
                # 调用 VTKViewer 的 load_dicom_series 方法
                self.vtk_viewer.load_dicom_series(folder_path)
            except Exception as e:
                print(f"体绘制失败: {e}")


if __name__ == "__main__":
    app = QApplication([])
    viewer = DicomViewer()
    viewer.show()
    app.exec_()