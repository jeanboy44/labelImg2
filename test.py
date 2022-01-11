try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import (
        QGroupBox,
        QGridLayout,
        QLineEdit,
        QDialog,
        QDialogButtonBox,
        QFormLayout,
        QProgressBar,
        QPushButton,
        QLabel,
    )
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

__appname__ = "labelImg"


class ExportFilesDialog(QDialog):
    def __init__(self, parent=None):
        super(ExportFilesDialog, self).__init__(parent)
        # Import functions

        # Define components
        self.entry = QLineEdit(self)
        self.entry_btn = QPushButton("browse")

        self.main_message1 = QLabel("Choose directory", self)
        self.main_message2 = QLabel("Export", self)
        self.pbar = QProgressBar(self)
        self.pbar_btn = QPushButton("Start", self)
        self.message = QLabel(self)

        # Deifine Actions
        self.entry_btn.clicked.connect(self.export_files_dir_dialog)
        self.pbar_btn.clicked.connect(self.doAction)

        # Define layouts
        layout_main = QFormLayout(self)
        layout1 = QGridLayout(self)
        layout2 = QGridLayout(self)
        layout1.addWidget(self.entry, 0, 0)
        layout1.addWidget(self.entry_btn, 0, 1)
        layout2.addWidget(self.pbar_btn, 0, 0)
        layout2.addWidget(self.pbar, 0, 1)
        layout_main.addRow(self.main_message1)
        layout_main.addRow(layout1)
        layout_main.addRow(self.main_message2)
        layout_main.addRow(layout2)
        # layout_main.addRow(self.pbar_btn)
        # layout_main.addRow(self.pbar)
        layout_main.addRow(self.message)

        self.setWindowTitle("Export Files")
        self.setGeometry(300, 300, 800, 200)

    def export_files_dir_dialog(self, dir_path=None, _value=False):
        path = "."

        self.export_dir = ustr(
            QFileDialog.getExistingDirectory(
                self,
                "%s - Export images and anntations to the directory" % __appname__,
                path,
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
            )
        )

        print("--------------")
        print(self.export_dir)
        self.statusBar().showMessage(
            f"Images and Annotation will be exported to {self.export_dir}"
        )
        self.statusBar().show()

    def getInputs(self):
        return (self.first.text(), self.second.text())

    def doAction(self):
        if self.btn.text() == "Finished":
            self.close()
        if self.btn.text() == "Stop":
            self.btn.setText("Start")
            self.pbar.setValue(0)
        else:
            self.btn.setText("Stop")
            current_label, replace_label = self.getInputs()

            try:
                file_list = self.label_image_dict[current_label]
            except:
                file_list = []

            print(current_label)
            print(replace_label)

            self.message.setText(f"{len(file_list)} files affected")

            self.pbar.setMaximum(len(file_list))
            for i, file_ in enumerate(file_list):
                shapes = self.load_labels_from_annotation_file(file_)
                for j, shp in enumerate(shapes):
                    if shp[0] == current_label:
                        shp = list(shp)
                        shp[0] = replace_label
                        shapes[j] = tuple(shp)
                self.save_labels_to_annotation_file(shapes, file_)
                self.pbar.setValue(i + 1)

            self.btn.setText("Finished")

            self.load_label_image_dict()
            self.update_all_label_combo_box()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    myWindow = ExportFilesDialog()
    myWindow.show()
    app.exec_()
