try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import (
        QMessageBox,
        QLineEdit,
        QDialog,
        QGridLayout,
        QFormLayout,
        QFileDialog,
        QProgressBar,
        QFileDialog,
        QPushButton,
        QLabel,
        QCheckBox,
    )
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

import os
import shutil
from libs.ustr import ustr
from libs.pascal_voc_io import XML_EXT
from libs.yolo_io import TXT_EXT
from libs.create_ml_io import JSON_EXT

__appname__ = "labelImg"


class ExportFilesDialog(QDialog):
    def __init__(self, parent=None):
        super(ExportFilesDialog, self).__init__(parent)
        # Import functions
        self.load_label_image_dict = parent.load_label_image_dict
        self.label_image_dict = parent.label_image_dict
        self.m_img_list_all = parent.m_img_list_all
        self.verified_image_list = parent.verified_image_list
        self.default_save_dir = parent.default_save_dir

        # Define components
        self.cb1 = QCheckBox("Verified files", self)
        self.cb2 = QCheckBox("Labeled files", self)
        self.entry = QLineEdit(self)
        self.entry_btn = QPushButton("browse")

        self.main_message0 = QLabel("Choose option", self)
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
        layout_main.addRow(self.main_message0)
        layout_main.addRow(self.cb1)
        layout_main.addRow(self.cb2)
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

        self.entry.setText(ustr(self.export_dir))

    def get_label_filepath(self, file_path):
        if self.default_save_dir is not None:
            basename = os.path.basename(os.path.splitext(file_path)[0])
            xml_path = os.path.join(self.default_save_dir, basename + XML_EXT)
            txt_path = os.path.join(self.default_save_dir, basename + TXT_EXT)
            json_path = os.path.join(self.default_save_dir, basename + JSON_EXT)

            label_path = None
            """Annotation file priority:
            PascalXML > YOLO
            """
            if os.path.isfile(xml_path):
                label_path = xml_path
            elif os.path.isfile(txt_path):
                label_path = txt_path
            elif os.path.isfile(json_path):
                label_path = json_path

        else:
            xml_path = os.path.splitext(file_path)[0] + XML_EXT
            txt_path = os.path.splitext(file_path)[0] + TXT_EXT
            if os.path.isfile(xml_path):
                label_path = xml_path
            elif os.path.isfile(txt_path):
                label_path = txt_path

        return label_path

    def doAction(self):
        if self.pbar_btn.text() == "Finished":
            self.close()
        if self.pbar_btn.text() == "Stop":
            self.pbar_btn.setText("Start")
            self.pbar.setValue(0)
        else:
            self.pbar_btn.setText("Stop")

            export_dir = self.entry.text()
            print(export_dir)
            if not os.path.isdir(export_dir):
                self.error_dialog = QMessageBox.critical(
                    self, "Invalid directory", "Invalid directory"
                )
                self.pbar_btn.setText("Start")
            else:
                self.load_label_image_dict()
                # select images with labels
                files_list = []
                if self.cb1.isChecked():
                    files_list += self.verified_image_list

                if self.cb2.isChecked():
                    for file_list_ in self.label_image_dict.values():
                        files_list += file_list_

                files_list = sorted(set(files_list))

                # copy files to dir
                srcfile_num = 0
                dstfile_num = 0
                os.makedirs(os.path.join(export_dir, "image"), exist_ok=True)
                os.makedirs(os.path.join(export_dir, "label"), exist_ok=True)
                self.pbar.setMaximum(len(files_list))
                for i, srcfile_img in enumerate(files_list):
                    filename_ = os.path.basename(srcfile_img)
                    dstfile_img = os.path.join(export_dir, "image", filename_)

                    srcfile_label = self.get_label_filepath(srcfile_img)
                    filename_ = os.path.basename(srcfile_label)
                    dstfile_label = os.path.join(export_dir, "label", filename_)
                    try:
                        shutil.copyfile(srcfile_label, dstfile_label)
                        # print(f"Annotation:{srcfile_label} -> {dstfile_label}")
                        srcfile_num += 1
                        shutil.copyfile(srcfile_img, dstfile_img)
                        # print(f"Image:{srcfile_img} -> {dstfile_img}")
                        dstfile_num += 1
                    except Exception as e:
                        print(e)
                    self.pbar.setValue(i + 1)

                self.message.setText(
                    f"{srcfile_num} images, {dstfile_num} annotations were moved."
                )

                self.pbar_btn.setText("Finished")
