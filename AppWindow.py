import PyQt5.QtWidgets as QtWidgets
from threading import Thread

from app.widgets.LandmarksSettingsWidgets import LandmarksSettingsWidgets
from app.widgets.PatientAxesViewWidget import PatientAxesViewWidget
from app.widgets.SegmentationSettingsWidget import SegmentationSettingsWidget
from app.widgets.SkullSettingsWidget import SkullSettingsWidget
from app.widgets.VtkWidget import VtkWidget

from vtkFeatures.VtkHandler import VtkHandler
from default_parameters import WINDOW_TITLE


class AppWindow(QtWidgets.QMainWindow, QtWidgets.QApplication):
    def __init__(self, app):
        self.app = app
        QtWidgets.QMainWindow.__init__(self, None)

        renderer, render_window, self.vtk_window, self.frame = self.setup()
        self.vtk_handler = VtkHandler(render_window, renderer)

        self.add_widgets()

        self.setWindowTitle(WINDOW_TITLE)
        self.frame.setLayout(self.grid)
        self.setCentralWidget(self.frame)
        self.showMaximized()

    @staticmethod
    def setup():
        frame = QtWidgets.QFrame()
        frame.setStyleSheet(open('styles.css').read())

        frame.setAutoFillBackground(True)

        renderer, render_window, vtk_window = VtkWidget.setup_vtk_window()

        return renderer, render_window, vtk_window, frame

    def add_widgets(self):
        self.add_menu_bar()
        self.grid = QtWidgets.QGridLayout()

        self.vtk_widget = VtkWidget(
            vtk_window=self.vtk_window,
            callback_clean_view=self.clean_view,
            parent_grid=self.grid
        )

        self.skull_settings_widget = SkullSettingsWidget(
            import_skull_callback=self.setup_skull,
            vtk_handler=self.vtk_handler,
            parent_grid=self.grid
        )

        self.segmentation_settings_widget = SegmentationSettingsWidget(
            vtk_handler=self.vtk_handler,
            parent_grid=self.grid)

        self.landmarks_settings_widget = LandmarksSettingsWidgets(
            detect_landmarks_callback=self.set_detected_landmarks,
            import_landmarks_callback=self.set_real_landmarks,
            parent_grid=self.grid
        )

        self.patient_axes_views_widget = PatientAxesViewWidget(
            vtk_handler=self.vtk_handler,
            parent_grid=self.grid
        )

    def add_menu_bar(self):
        menu_bar = self.menuBar()

        # Export menu button
        export_menu = menu_bar.addMenu("&Exportar")

        export_landmarks_action = QtWidgets.QAction(
            "Exportar pontos fiduciais", self)
        export_landmarks_action.triggered.connect(
            lambda _: None)
        export_menu.addAction(export_landmarks_action)

    def setup_skull(self, path: str):
        is_nifti_file = path.endswith("nii.gz")
        
        if is_nifti_file:
            self.vtk_handler.setup_skull_from_nifti_file(path)
            self.segmentation_settings_widget.segmentate_button.setHidden(True)
        else:
            self.vtk_handler.setup_skull_from_dicom_dir(path)
            self.segmentation_settings_widget.segmentate_button.setHidden(
                False)

        # show skull opacity slider
        self.skull_settings_widget.skull_opacity_slider.setHidden(False)
        self.skull_settings_widget.skull_opacity_slider.label_instance.setHidden(
            False)

        # show detect landmarks button
        self.landmarks_settings_widget.detect_landmarks_button.setHidden(False)
        self.landmarks_settings_widget.detect_landmarks_button_label.setHidden(
            False)

        # update vtk window title
        self.vtk_widget.set_vtk_window_title(
            f"Visualização do crânio: {self.vtk_handler.get_skull_volume_data().patient_name}")
        self.vtk_handler.set_sagittal_view()

    def set_real_landmarks(self, file_path):
        self.real_landmarks = self.vtk_handler.setup_imported_landmarks(
            file_path)
        self.vtk_handler.set_sagittal_view()

    def set_detected_landmarks(self):
        thread = Thread(target=self.detected_landmarks)
        thread.start()
        # update vtk window title
        self.vtk_widget.set_vtk_window_title(
            f"Visualização do crânio: {self.vtk_handler.get_skull_volume_data().patient_name} \t\t\t\t\t\t Detectando pontos fiduciais...")

    def detected_landmarks(self):
        self.real_landmarks, self.detected_landmarks = self.vtk_handler.setup_landmarks_detection(
            self.vtk_handler.get_skull_volume_data().nifti_path)

        self.vtk_handler.set_sagittal_view()

        # update vtk window title
        self.vtk_widget.set_vtk_window_title(
            f"Visualização do crânio: {self.vtk_handler.get_skull_volume_data().patient_name} \t\t\t\t\t\t Pontos fiduciais detectados!")

    def clean_view(self):
        # reset segmentation labels
        self.segmentation_settings_widget.reset_values()
        self.skull_settings_widget.reset_values()
        self.vtk_widget.reset_values()
        self.landmarks_settings_widget.reset_values()

        # update vtk view
        self.vtk_handler.reset_vtk_window()
