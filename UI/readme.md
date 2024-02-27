        self.range_slider = QRangeSlider(QtCore.Qt.Horizontal, self.Editing)
        self.range_slider.setMinimumSize(QtCore.QSize(600, 20))
        self.range_slider.setMaximumSize(QtCore.QSize(600, 20))
        self.range_slider.setStyleSheet("QSlider::groove:horizontal {\n"
"    border: 1px solid #999999;\n"
"    height: 15px; \n"
"    background: rgb(255, 255, 255);\n"
"    border-radius:3px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"    background:  rgb(0, 0, 0);\n"
"    border: 1px solid #5c5c5c;\n"
"    width: 10px;\n"
"    margin: -5px 0;\n"
"    border-radius: 9px;\n"
"}")
        self.range_slider.setMaximum(999)
        self.range_slider.setPageStep(0)
        self.range_slider.setOrientation(QtCore.Qt.Horizontal)
        self.range_slider.setObjectName("range_slider")
        self.verticalLayout_6.addWidget(self.range_slider)