# coding:utf-8
import sys
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

import core


# 先使用pyside

# Section
class FrameLayoutTitle(QtGui.QWidget):
    def __init__(self, name=None, parent=None):
        super(FrameLayoutTitle, self).__init__(parent)
        self.setFixedHeight(20)
        # # 貌似用widget的size policy比layout的size constraint实现效果好
        # self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)

        self.mainLayout = QtGui.QHBoxLayout()
        # self.mainLayout.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)

        self.toolButton = QtGui.QToolButton()
        self.toolButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        self.toolButton.setText(name)

        self.editor = QtGui.QLineEdit()

        self.editor.editingFinished.connect(self.finishRename)
        self.editor.returnPressed.connect(self.finishRename)

        self.mainLayout.addWidget(self.toolButton)
        self.mainLayout.addWidget(self.editor)

        self.editor.setHidden(True)

    def mouseDoubleClickEvent(self, event):
        # self.mainLayout.setCurrentIndex(1)
        self.toolButton.setHidden(True)
        self.editor.setHidden(False)

        self.editor.setFocus()
        text = self.toolButton.text()
        self.editor.setText(text)
        self.editor.selectAll()
        # self.adjustSize()
        # self.update()

    def finishRename(self):
        # self.mainLayout.setCurrentIndex(0)
        self.toolButton.setHidden(False)
        self.editor.setHidden(True)

        text = self.editor.text()
        self.toolButton.setText(text)
        # self.toolButton.setFocus()
        # self.adjustSize()
        # self.update()

    def button(self):
        return self.toolButton


class FrameLayoutWidget(QtGui.QDialog):
    def __init__(self, name=None):
        super(FrameLayoutWidget, self).__init__()
        self.vlayout = QtGui.QVBoxLayout()
        self.vlayout.setSpacing(0)
        self.vlayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.vlayout)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.setSpacing(0)

        self.title = FrameLayoutTitle(name)
        self.title.button().setArrowType(QtCore.Qt.RightArrow)
        self.title.button().setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        self.vlayout.addWidget(self.title)

        # 塌陷
        self.collapse = True
        self.mainbody = QtGui.QFrame()
        self.mainbody.setMinimumHeight(10)
        self.mainbody.setHidden(True)
        self.vlayout.addWidget(self.mainbody)
        self.setSignals()

        self.vlayout.addStretch(2)

    def setSignals(self):
        self.title.button().clicked.connect(self.setCollapse)

    def setCollapse(self):

        self.collapse = not self.collapse
        self.mainbody.setHidden(self.collapse)
        if self.collapse:
            self.title.button().setArrowType(QtCore.Qt.RightArrow)
        else:
            self.title.button().setArrowType(QtCore.Qt.DownArrow)

        # 刷新措施 得在变化后刷新
        # self.title.adjustSize()
        # self.title.update()

        # self.adjustSize()
        self.update()
        if self.parent():
            try:
                # self.parent().adjustSize()
                self.parent().update()
            except Exception:
                pass


# 要添加功能,
# 编辑标题栏
class SectionWidget(FrameLayoutWidget):
    def __init__(self, name=None):
        super(SectionWidget, self).__init__(name)
        self.section_name = self.title.button().text()

        self.mainbodyLayout = QtGui.QVBoxLayout()
        self.mainbodyLayout.setContentsMargins(0, 0, 0, 0)
        self.mainbodyLayout.setSpacing(0)
        self.mainbody.setLayout(self.mainbodyLayout)

        self.add_option_button = QtGui.QPushButton("Add")
        self.mainbodyLayout.addWidget(self.add_option_button)
        self.add_option_button.clicked.connect(self.add_option)

        self.installEventFilter(self)

    def add_option(self):
        default_temp_option = OptionWidget("default", "")
        self.mainbodyLayout.insertWidget(0, default_temp_option)
        default_temp_option.setFocus()
        print self.sender()

    def remove_option(self):
        pass

    def eventFilter(self, object, event):
        # print object, type(object), event.type()
        # if event.type().__str__().split(".")[-1].startswith("Mouse"):
        #     print event.type()
        return super(SectionWidget, self).eventFilter(object, event)


# Option

class OptionLabel(QtGui.QWidget):
    def __init__(self, name=None, parent=None):
        super(OptionLabel, self).__init__(parent=parent)
        self.setFixedHeight(20)
        self.mainLayout = QtGui.QHBoxLayout()

        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)

        self.label = QtGui.QLabel(name)
        self.mainLayout.addWidget(self.label)

        self.labelEditor = QtGui.QLineEdit()
        self.labelEditor.setVisible(False)
        self.labelEditor.editingFinished.connect(self.finishRename)
        self.labelEditor.returnPressed.connect(self.finishRename)
        self.mainLayout.addWidget(self.labelEditor)

    def mouseDoubleClickEvent(self, event):
        self.label.setHidden(True)
        self.labelEditor.setHidden(False)

        self.labelEditor.setFocus()
        text = self.label.text()
        self.labelEditor.setText(text)
        self.labelEditor.selectAll()

    def finishRename(self):
        self.label.setHidden(False)
        self.labelEditor.setHidden(True)

        text = self.labelEditor.text()
        self.label.setText(text)


class OptionWidget(QtGui.QWidget):
    def __init__(self, label=None, data=None, default=None, parent=None):
        super(OptionWidget, self).__init__(parent)
        self.mainlayout = QtGui.QHBoxLayout()
        self.mainlayout.setContentsMargins(0, 0, 0, 0)
        self.mainlayout.setSpacing(0)
        self.setLayout(self.mainlayout)

        self.label = OptionLabel(label)
        self.label.setFixedWidth(100)
        self.mainlayout.addWidget(self.label)

        # space
        self.mainlayout.addStretch(0)

        # data widgets

        # 里面的全是字符串 enum
        self.data_enum = QtGui.QComboBox()
        # values = [x.name for x in Enum.__members__] # self.data_widget.addItems(values)
        # self.data_enum.setMinimumWidth(80)

        self.data_int = QtGui.QSpinBox()
        self.data_int.setMinimum(0)
        self.data_int.setMaximum(100)
        # self.data_int.setMinimumWidth(80)

        self.data_float = QtGui.QDoubleSpinBox()
        self.data_float.setMinimum(0)
        self.data_float.setMaximum(1)
        # self.data_float.setMinimumWidth(80)

        self.data_bool = QtGui.QCheckBox()
        self.data_bool.setChecked(False)
        # self.data_bool.setMinimumWidth(80)

        self.data_string = QtGui.QLineEdit()
        self.data_string.setPlaceholderText("some string")
        # self.data_string.setMinimumWidth(80)

        self.mainlayout.addWidget(self.data_enum)
        self.data_enum.setVisible(False)
        self.mainlayout.addWidget(self.data_int)
        self.data_int.setVisible(False)
        self.mainlayout.addWidget(self.data_float)
        self.data_float.setVisible(False)
        self.mainlayout.addWidget(self.data_bool)
        self.data_bool.setVisible(False)
        self.mainlayout.addWidget(self.data_string)
        self.data_string.setVisible(False)

        self._process_visible(data, default)
        # data
        self.name = label
        self.value = None
        self.type = None

        # 处理信号
        self.data_enum.currentIndexChanged[int].connect(self._process_value)
        self.data_int.valueChanged[int].connect(self._process_value)
        self.data_float.valueChanged[float].connect(self._process_value)
        self.data_bool.stateChanged.connect(self._process_value)
        self.data_string.editingFinished.connect(self._process_value)
        self.data_string.returnPressed.connect(self._process_value)

        self.label.labelEditor.editingFinished.connect(self._process_name)
        self.label.labelEditor.returnPressed.connect(self._process_name)

    def _process_visible(self, data, default=None):
        if default:
            if type(default) == tuple and isinstance(data, basestring):
                self.data_enum.setVisible(True)
                self.data_enum.addItems(default)
                self.data_enum.setCurrentIndex(self.data_enum.findText(data, QtCore.Qt.MatchExactly))
                self.type = "ENUM"
        else:
            if type(data) == int:
                self.data_int.setVisible(True)
                self.data_int.setValue(data)
                self.type = "INT"
            if type(data) == float:
                self.data_float.setVisible(True)
                self.data_float.setValue(data)
                self.type = "FLOAT"
            if type(data) == bool:
                self.data_bool.setVisible(True)
                self.data_bool.setChecked(True)
                self.type = "BOOLEAN"
            if isinstance(data, basestring):
                self.data_string.setVisible(True)
                self.data_string.setText(data)
                self.type = "STRING"

    def _process_value(self, *argv):
        if self.sender() == self.data_enum:
            self.value = self.data_enum.itemText(argv[0])
        if self.sender() == self.data_int:
            self.value = argv[0]
        if self.sender() == self.data_float:
            self.value = argv[0]
        if self.sender() == self.data_bool:
            self.value = True if argv[0] else False
        if self.sender() == self.data_string:
            self.value = self.data_string.text()

        print self.value

    def _process_name(self, *args):
        self.name = self.label.label.text()
        print self.name

    def request_options(self):
        # 生成opiton objects
        if self.type == "ENUM":
            option_value = core.OptionObject(self.name, self.value)
            texts = [self.data_enum.itemText(x) for x in xrange(self.data_enum.count())]
            option_available_values = core.OptionObject(self.name + "_options", texts)
            return [option_value, option_available_values]
        if self.type in {"INT", "FLOAT", "BOOLEAN", "STRING"}:
            option_value = core.OptionObject(self.name, self.value)
            return [option_value]
        return []


if __name__ == '__main__':
    myapp = QtGui.QApplication(sys.argv)

    # ui = FrameLayoutTitle()
    # ui.show()


    # ui = OptionWidget("ff", "2015", ("2008", "2009", "2010", "2015", "2017"))
    # ui.show()

    # ui = OptionLabel("fff")
    # ui.show()

    ui = SectionWidget("ff")
    ui.show()


    myapp.exec_()
