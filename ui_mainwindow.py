# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QMainWindow,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1270, 730)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.c_method_comboBox = QComboBox(self.centralwidget)
        self.c_method_comboBox.addItem("")
        self.c_method_comboBox.addItem("")
        self.c_method_comboBox.addItem("")
        self.c_method_comboBox.addItem("")
        self.c_method_comboBox.setObjectName(u"c_method_comboBox")

        self.horizontalLayout_3.addWidget(self.c_method_comboBox)

        self.pushButton_5 = QPushButton(self.centralwidget)
        self.pushButton_5.setObjectName(u"pushButton_5")

        self.horizontalLayout_3.addWidget(self.pushButton_5)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.left_load_file = QPushButton(self.centralwidget)
        self.left_load_file.setObjectName(u"left_load_file")

        self.horizontalLayout_5.addWidget(self.left_load_file)

        self.left_clear_area = QPushButton(self.centralwidget)
        self.left_clear_area.setObjectName(u"left_clear_area")

        self.horizontalLayout_5.addWidget(self.left_clear_area)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)


        self.verticalLayout_4.addLayout(self.horizontalLayout_5)

        self.left_viewer = QScrollArea(self.centralwidget)
        self.left_viewer.setObjectName(u"left_viewer")
        self.left_viewer.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 510, 638))
        self.left_viewer.setWidget(self.scrollAreaWidgetContents_3)

        self.verticalLayout_4.addWidget(self.left_viewer)


        self.horizontalLayout_4.addLayout(self.verticalLayout_4)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.right_load_file = QPushButton(self.centralwidget)
        self.right_load_file.setObjectName(u"right_load_file")

        self.horizontalLayout_6.addWidget(self.right_load_file)

        self.right_clear_area = QPushButton(self.centralwidget)
        self.right_clear_area.setObjectName(u"right_clear_area")

        self.horizontalLayout_6.addWidget(self.right_clear_area)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_2)


        self.verticalLayout_5.addLayout(self.horizontalLayout_6)

        self.right_viewer = QScrollArea(self.centralwidget)
        self.right_viewer.setObjectName(u"right_viewer")
        self.right_viewer.setWidgetResizable(True)
        self.scrollAreaWidgetContents_4 = QWidget()
        self.scrollAreaWidgetContents_4.setObjectName(u"scrollAreaWidgetContents_4")
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 510, 638))
        self.right_viewer.setWidget(self.scrollAreaWidgetContents_4)

        self.verticalLayout_5.addWidget(self.right_viewer)


        self.horizontalLayout_4.addLayout(self.verticalLayout_5)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)


        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.prev_button = QPushButton(self.centralwidget)
        self.prev_button.setObjectName(u"prev_button")

        self.horizontalLayout_2.addWidget(self.prev_button)

        self.next_button = QPushButton(self.centralwidget)
        self.next_button.setObjectName(u"next_button")

        self.horizontalLayout_2.addWidget(self.next_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.changes_viewer = QScrollArea(self.centralwidget)
        self.changes_viewer.setObjectName(u"changes_viewer")
        self.changes_viewer.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 203, 674))
        self.changes_viewer.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_2.addWidget(self.changes_viewer)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.horizontalLayout.setStretch(0, 5)
        self.horizontalLayout.setStretch(1, 1)

        self.verticalLayout.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.c_method_comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Myers Diff (Default)", None))
        self.c_method_comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"DeepDiff", None))
        self.c_method_comboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"Placeholder", None))
        self.c_method_comboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"Placeholder22", None))

        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"Compare", None))
        self.left_load_file.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.left_clear_area.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.right_load_file.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.right_clear_area.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.prev_button.setText(QCoreApplication.translate("MainWindow", u"Prev", None))
        self.next_button.setText(QCoreApplication.translate("MainWindow", u"Next", None))
    # retranslateUi

