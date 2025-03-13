import os
import vtk
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QToolBar, QAction, QSlider, QLabel
from PyQt5.QtCore import Qt
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class VTKViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D 可视化")
        self.setGeometry(100, 100, 800, 600)

        # VTK 渲染窗口
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.vtk_widget)
        self.setLayout(self.layout)

        # 初始化渲染器和交互器
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)

        # 设置交互器样式
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

        # 初始化 DICOM 读取器
        self.reader = vtk.vtkDICOMImageReader()

        # 初始化体积映射器
        self.mapper = vtk.vtkFixedPointVolumeRayCastMapper()
        self.mapper.SetInputConnection(self.reader.GetOutputPort())

        # 初始化体积属性
        self.volume_property = vtk.vtkVolumeProperty()
        self.volume_property.ShadeOn()
        self.volume_property.SetInterpolationTypeToLinear()

        # 初始化体积对象
        self.volume = vtk.vtkVolume()
        self.volume.SetMapper(self.mapper)
        self.volume.SetProperty(self.volume_property)

        # 添加体积到渲染器
        self.renderer.AddVolume(self.volume)

        # 初始化切片查看器
        self.slice_widget = None

        # 添加工具栏
        self.toolbar = QToolBar("工具", self)
        self.layout.addWidget(self.toolbar)

        # 添加工具栏按钮
        self.add_toolbar_buttons()

    def add_toolbar_buttons(self):
        """添加工具栏按钮"""
        # 切片查看按钮
        self.slice_action = QAction("切片查看", self)
        self.slice_action.triggered.connect(self.enable_slice_view)
        self.toolbar.addAction(self.slice_action)

        # 透明度调整滑块
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(50)
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        self.toolbar.addWidget(QLabel("透明度:"))
        self.toolbar.addWidget(self.opacity_slider)

    def load_dicom_series(self, directory):
        """加载 DICOM 序列并进行 3D 渲染"""
        try:
            # 检查目录是否存在
            if not os.path.isdir(directory):
                raise ValueError(f"目录不存在: {directory}")

            # 检查目录中是否有 DICOM 文件
            dicom_files = [f for f in os.listdir(directory) if f.endswith(".dcm")]
            if not dicom_files:
                raise ValueError(f"目录中没有 DICOM 文件: {directory}")

            # 读取 DICOM 文件
            self.reader.SetDirectoryName(directory)
            self.reader.Update()

            # 设置透明度函数和颜色传输函数
            self.setup_transfer_functions()

            # 重置相机并渲染
            self.renderer.ResetCamera()
            self.vtk_widget.GetRenderWindow().Render()
            print("DICOM 序列加载成功！")
        except Exception as e:
            print(f"加载 DICOM 序列失败: {e}")

    def setup_transfer_functions(self):
        """设置透明度函数和颜色传输函数（针对肺部数据）"""
        # 透明度函数
        opacity_function = vtk.vtkPiecewiseFunction()
        opacity_function.AddPoint(-1000, 0.0)  # 空气（完全透明）
        opacity_function.AddPoint(-600, 0.0)   # 肺部组织（开始显示）
        opacity_function.AddPoint(-400, 0.2)   # 肺部组织（半透明）
        opacity_function.AddPoint(0, 0.5)      # 软组织（较清晰）
        opacity_function.AddPoint(300, 0.8)    # 骨骼（较不透明）
        opacity_function.AddPoint(1000, 1.0)   # 高密度组织（完全不透明）

        # 颜色传输函数
        color_function = vtk.vtkColorTransferFunction()
        color_function.AddRGBPoint(-1000, 0.0, 0.0, 0.0)  # 空气（黑色）
        color_function.AddRGBPoint(-600, 0.0, 0.5, 1.0)   # 肺部组织（蓝色）
        color_function.AddRGBPoint(-400, 0.0, 1.0, 0.5)   # 肺部组织（青色）
        color_function.AddRGBPoint(0, 1.0, 1.0, 0.0)      # 软组织（黄色）
        color_function.AddRGBPoint(300, 1.0, 0.5, 0.0)    # 骨骼（橙色）
        color_function.AddRGBPoint(1000, 1.0, 0.0, 0.0)   # 高密度组织（红色）

        # 设置体积属性
        self.volume_property.SetColor(color_function)
        self.volume_property.SetScalarOpacity(opacity_function)

    def enable_slice_view(self):
        """启用切片查看功能"""
        if self.slice_widget is None:
            # 创建切片查看器
            self.slice_widget = vtk.vtkImagePlaneWidget()
            self.slice_widget.SetInteractor(self.interactor)
            self.slice_widget.SetInputConnection(self.reader.GetOutputPort())
            self.slice_widget.SetPlaneOrientationToXAxes()  # 默认显示 X 轴切面
            self.slice_widget.On()

    def update_opacity(self, value):
        """更新透明度（针对肺部数据）"""
        opacity = value / 100.0
        opacity_function = self.volume_property.GetScalarOpacity()
        opacity_function.RemoveAllPoints()
        opacity_function.AddPoint(-1000, 0.0)  # 空气（完全透明）
        opacity_function.AddPoint(-600, 0.0 * opacity)   # 肺部组织（开始显示）
        opacity_function.AddPoint(-400, 0.2 * opacity)   # 肺部组织（半透明）
        opacity_function.AddPoint(0, 0.5 * opacity)      # 软组织（较清晰）
        opacity_function.AddPoint(300, 0.8 * opacity)    # 骨骼（较不透明）
        opacity_function.AddPoint(1000, 1.0 * opacity)   # 高密度组织（完全不透明）
        self.vtk_widget.GetRenderWindow().Render()