try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import (
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


class RenameLabelDialog(QDialog):
    def __init__(self, parent=None):
        super(RenameLabelDialog, self).__init__(parent)

        self.label_image_dict = parent.label_image_dict
        self.load_labels_from_annotation_file = parent.load_labels_from_annotation_file
        self.save_labels_to_annotation_file = parent.save_labels_to_annotation_file
        self.load_label_image_dict = parent.load_label_image_dict
        self.update_all_label_combo_box = parent.update_all_label_combo_box
        self.first = QLineEdit(self)
        self.second = QLineEdit(self)

        self.pbar = QProgressBar(self)
        self.message = QLabel(self)

        self.btn = QPushButton("Start", self)
        # self.btn.move(40, 80)
        self.btn.clicked.connect(self.doAction)

        layout = QFormLayout(self)
        layout.addRow("Search For", self.first)
        layout.addRow("Replace With", self.second)
        layout.addWidget(self.btn)
        layout.addWidget(self.pbar)
        layout.addWidget(self.message)

        # self.timer = QBasicTimer()
        # self.step = 0

        self.setWindowTitle("Rename Labels")
        self.setGeometry(300, 300, 300, 200)

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
