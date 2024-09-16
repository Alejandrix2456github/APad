import sys
import os
import importlib.util
from PyQt5.QtWidgets import QApplication, QCheckBox, QInputDialog, QMainWindow, QAction, QFileDialog, QTextEdit, QTabWidget, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout, QToolBar, QMessageBox, QStatusBar, QSplitter, QLabel, QDialog, QDialogButtonBox
from PyQt5.QtGui import QIcon, QFont, QColor, QSyntaxHighlighter, QTextCharFormat, QPainter, QPalette
from PyQt5.QtCore import Qt, QRegExp, QProcess, QStringListModel
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
import os
import subprocess  # For Git commands
import sys
import os

import sys
import os
import importlib.util


def closeEvent(self, event):
        for i in range(self.tabWidget.count()):
            if self.isTabModified(i):
                response = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    f"The document in tab {i+1} has unsaved changes. Do you want to save them?",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )

                if response == QMessageBox.Yes:
                    self.saveFile()
                elif response == QMessageBox.Cancel:
                    event.ignore()
                    return  # Don't close the application
        event.accept()  # Close the application if all tabs are saved or user chooses not to save

def isTabModified(self, index):
        """Checks if the tab at the given index is modified."""
        widget = self.tabWidget.widget(index)
        if widget:
            textEdit = widget.findChild(QTextEdit)
            if textEdit:
                return textEdit.document().isModified()
        return False



class TextEditor(QMainWindow):
    # ... (other methods) ...

    def openFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'All Files (*);;Text files (*.txt)', options=options)
        if fileName:
            with open(fileName, 'r') as file:
                content = file.read()
            newTab = QWidget()
            layout = QVBoxLayout()
            textEdit = QTextEdit()
            textEdit.setText(content)
            layout.addWidget(textEdit)
            newTab.setLayout(layout)

            # --- Change here ---
            file_name_only = os.path.basename(fileName)  # Extract filename only
            self.tabWidget.addTab(newTab, file_name_only) 
            # ---------------------

            self.tabWidget.setCurrentWidget(newTab)

            highlighter = SyntaxHighlighter(textEdit.document())

            # ... (rest of your openFile method) ...

    def saveFile(self):
        currentWidget = self.tabWidget.currentWidget()
        if currentWidget:
            textEdit = currentWidget.findChild(QTextEdit)
            if textEdit:
                options = QFileDialog.Options()
                fileName, _ = QFileDialog.getSaveFileName(self, 'Save Files', '', 'All Files (*);;Text Files (*.txt)', options=options)
                if fileName:
                    with open(fileName, 'w') as file:
                        file.write(textEdit.toPlainText())

                    # --- Change here ---
                    current_index = self.tabWidget.currentIndex()
                    file_name_only = os.path.basename(fileName)
                    self.tabWidget.setTabText(current_index, file_name_only)
                    # ---------------------


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(SyntaxHighlighter, self).__init__(parent)
        self.highlightingRules = []

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor("blue"))
        keywordPatterns = ["\bchar\b", "\bclass\b", "\bconst\b", "\bdouble\b", "\benum\b",
                           "\bexplicit\b", "\bfriend\b", "\binline\b", "\bint\b", "\blong\b",
                           "\bnamespace\b", "\boperator\b", "\bprivate\b", "\bprotected\b",
                           "\bpublic\b", "\bshort\b", "\bsignals\b", "\bsigned\b", "\bslots\b",
                           "\bstatic\b", "\bstruct\b", "\btemplate\b", "\btypedef\b", "\btypename\b",
                           "\bunion\b", "\bunsigned\b", "\bvirtual\b", "\bvoid\b", "\bvolatile\b"]
        for pattern in keywordPatterns:
            self.highlightingRules.append((QRegExp(pattern), keywordFormat))

        singleLineCommentFormat = QTextCharFormat()
        singleLineCommentFormat.setForeground(QColor("green"))
        self.highlightingRules.append((QRegExp("//[^\n]*"), singleLineCommentFormat))

        quotationFormat = QTextCharFormat()
        quotationFormat.setForeground(QColor("red"))
        self.highlightingRules.append((QRegExp("\".*\""), quotationFormat))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")

        self.findLabel = QLabel("Find:")
        self.findLineEdit = QLineEdit()
        self.replaceLabel = QLabel("Replace with:")
        self.replaceLineEdit = QLineEdit()

        self.caseSensitiveCheckBox = QCheckBox("Case sensitive")
        self.wholeWordsCheckBox = QCheckBox("Whole words only")

        self.findNextButton = QPushButton("Find Next")
        self.replaceButton = QPushButton("Replace")
        self.replaceAllButton = QPushButton("Replace All")

        buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.findLabel)
        layout.addWidget(self.findLineEdit)
        layout.addWidget(self.replaceLabel)
        layout.addWidget(self.replaceLineEdit)
        layout.addWidget(self.caseSensitiveCheckBox)
        layout.addWidget(self.wholeWordsCheckBox)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.findNextButton)
        buttonLayout.addWidget(self.replaceButton)
        buttonLayout.addWidget(self.replaceAllButton)
        layout.addLayout(buttonLayout)

        layout.addWidget(buttonBox)
        self.setLayout(layout)

class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.plugins = {}
        self.loadPlugins()

    def initUI(self):
        self.setWindowTitle('APad')
        self.setGeometry(100, 100, 1200, 800)

        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.createActions()
        self.createMenus()
        self.createToolBar()

        self.show()

    def createActions(self):
        self.newAct = QAction('New', self, shortcut='Ctrl+N', triggered=self.newFile)
        self.openAct = QAction('Open...', self, shortcut='Ctrl+O', triggered=self.openFile)
        self.saveAct = QAction('Save', self, shortcut='Ctrl+S', triggered=self.saveFile)
        self.printAct = QAction('Print...', self, shortcut='Ctrl+P', triggered=self.printFile)
        self.runAct = QAction('Run Code', self, shortcut='Ctrl+R', triggered=self.runCode)
        self.exitAct = QAction('Exit', self, shortcut='Ctrl+Q', triggered=self.close)

        self.undoAct = QAction('Undo', self, shortcut='Ctrl+Z', triggered=self.undo)
        self.redoAct = QAction('Redo', self, shortcut='Ctrl+Y', triggered=self.redo)
        self.findAct = QAction('Search', self, shortcut='Ctrl+F', triggered=self.findText)
        self.macroAct = QAction('Run Macro', self, shortcut='Ctrl+M', triggered=self.runMacro)

        self.goToLineAct = QAction('Go to Line...', self, shortcut='Ctrl+G', triggered=self.goToLine)
        self.findReplaceAct = QAction('Find and Replace...', self, shortcut='Ctrl+H', triggered=self.findAndReplace)
        self.gitCloneAct = QAction('Git Clone...', self, triggered=self.gitClone)


    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu('File')
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = self.menuBar().addMenu('Edit')
        self.editMenu.addAction(self.undoAct)
        self.editMenu.addAction(self.redoAct)
        self.editMenu.addAction(self.findAct)
        self.editMenu.addAction(self.macroAct)
        self.editMenu.addAction(self.goToLineAct)
        self.editMenu.addAction(self.findReplaceAct)

        self.toolsMenu = self.menuBar().addMenu('Tools')
        self.loadPlugins()  # Load plugins when the menu is created

        self.gitMenu = self.menuBar().addMenu('Git')
        self.gitMenu.addAction(self.gitCloneAct)

        self.helpMenu = self.menuBar().addMenu('Help')  # Add Help menu
        self.helpMenu.addAction('About', self.about)  # Add About action
        
    def createToolBar(self):
        self.toolBar = QToolBar()
        self.addToolBar(self.toolBar)
        self.toolBar.addAction(self.newAct)
        self.toolBar.addAction(self.openAct)
        self.toolBar.addAction(self.saveAct)
        self.toolBar.addAction(self.printAct)
        self.toolBar.addAction(self.runAct)
        self.toolBar.addAction(self.undoAct)
        self.toolBar.addAction(self.redoAct)
        self.fileMenu.addAction(self.newAct)

    def newFile(self):
        newTab = QWidget()
        layout = QVBoxLayout()
        textEdit = QTextEdit() 
        layout.addWidget(textEdit)
        newTab.setLayout(layout)
        self.tabWidget.addTab(newTab, 'New Document')
        self.tabWidget.setCurrentWidget(newTab)

        highlighter = SyntaxHighlighter(textEdit.document())

        # Actualizar barra de estado
        textEdit.cursorPositionChanged.connect(self.updateStatusBar)

    def openFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'All Files (*);;Text files (*.txt)', options=options)
        if fileName:
            with open(fileName, 'r') as file:
                content = file.read()
            newTab = QWidget()
            layout = QVBoxLayout()
            textEdit = QTextEdit()
            textEdit.setText(content)
            layout.addWidget(textEdit)
            newTab.setLayout(layout)
            self.tabWidget.addTab(newTab, fileName)
            self.tabWidget.setCurrentWidget(newTab)

            highlighter = SyntaxHighlighter(textEdit.document())

            # Actualizar barra de estado
            textEdit.cursorPositionChanged.connect(self.updateStatusBar)

    def saveFile(self):
        currentWidget = self.tabWidget.currentWidget()
        if currentWidget:
            textEdit = currentWidget.findChild(QTextEdit)
            if textEdit:
                options = QFileDialog.Options()
                fileName, _ = QFileDialog.getSaveFileName(self, 'Save Files', '', 'All Files (*);;Text Files (*.txt)', options=options)
                if fileName:
                    with open(fileName, 'w') as file:
                        file.write(textEdit.toPlainText())

                    # --- Change here ---
                    current_index = self.tabWidget.currentIndex()
                    file_name_only = os.path.basename(fileName)
                    self.tabWidget.setTabText(current_index, file_name_only)
                    # ---------------------



    def printFile(self):
        currentWidget = self.tabWidget.currentWidget()
        if currentWidget:
            textEdit = currentWidget.findChild(QTextEdit)
            if textEdit:
                printer = QPrinter()
                dialog = QPrintDialog(printer, self)
                if dialog.exec_() == QPrintDialog.Accepted:
                    textEdit.print_(printer)

    def runCode(self):
        currentWidget = self.tabWidget.currentWidget()
        if currentWidget:
            textEdit = currentWidget.findChild(QTextEdit)
            if textEdit:
                code = textEdit.toPlainText()
                process = QProcess(self)
                process.start("python", ["-c", code])
                process.waitForFinished()
                output = process.readAllStandardOutput().data().decode()
                error = process.readAllStandardError().data().decode()
                QMessageBox.information(self, "Output", f"Output:\n{output}\nError:\n{error}")

    def undo(self):
        currentWidget = self.tabWidget.currentWidget()
        if currentWidget:
            textEdit = currentWidget.findChild(QTextEdit)
            if textEdit:
                textEdit.undo()

    def redo(self):
        currentWidget = self.tabWidget.currentWidget()
        if currentWidget:
            textEdit = currentWidget.findChild(QTextEdit)
            if textEdit:
                textEdit.redo()

    def findText(self):
        findDialog = QWidget()
        layout = QVBoxLayout()
        findInput = QLineEdit()
        findButton = QPushButton('Search')
        layout.addWidget(findInput)
        layout.addWidget(findButton)
        findDialog.setLayout(layout)
        findDialog.setWindowTitle('Search')
        findDialog.setGeometry(300, 300, 300, 100)
        findDialog.show()

        def search():
            text = findInput.text()
            currentWidget = self.tabWidget.currentWidget()
            if currentWidget:
                textEdit = currentWidget.findChild(QTextEdit)
                if textEdit:
                    textEdit.find(text)

        findButton.clicked.connect(search)

    def runMacro(self):
        currentWidget = self.tabWidget.currentWidget()
        if currentWidget:
            textEdit = currentWidget.findChild(QTextEdit)
            if textEdit:
                QMessageBox.information(self, "Macro", "Macro function is in development yet.")

    def goToLine(self):
        currentWidget = self.tabWidget.currentWidget()
        if currentWidget:
            textEdit = currentWidget.findChild(QTextEdit)
            if textEdit:
                lineNum, ok = QInputDialog.getInt(self, "Go to Line", "Enter line number:")
                if ok and lineNum > 0:
                    cursor = textEdit.textCursor()
                    cursor.movePosition(cursor.Start)
                    cursor.movePosition(cursor.Down, cursor.MoveAnchor, lineNum - 1)
                    textEdit.setTextCursor(cursor)

    def findAndReplace(self):
        dialog = FindReplaceDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            findText = dialog.findLineEdit.text()
            replaceText = dialog.replaceLineEdit.text()
            options = QTextEdit.FindFlags()

            if dialog.caseSensitiveCheckBox.isChecked():
                options |= QTextEdit.FindCaseSensitively

            if dialog.wholeWordsCheckBox.isChecked():
                options |= QTextEdit.FindWholeWords

            currentWidget = self.tabWidget.currentWidget()
            if currentWidget:
                textEdit = currentWidget.findChild(QTextEdit)
                if textEdit:
                    if not textEdit.find(findText, options):
                        QMessageBox.information(self, "Find and Replace", f"Cannot find '{findText}'")
                        return

                    if dialog.replaceAllButton.isChecked():
                        while textEdit.find(findText, options):
                            textEdit.textCursor().insertText(replaceText)
                    else:
                        textEdit.textCursor().insertText(replaceText)

    def gitClone(self):
        repoUrl, ok = QInputDialog.getText(self, "Git Clone", "Enter repository URL:")
        if ok:
            currentDir = os.getcwd()
            os.makedirs("cloned_repos", exist_ok=True)
            os.chdir("cloned_repos")
            try:
                subprocess.run(["git", "clone", repoUrl], check=True)
                QMessageBox.information(self, "Git Clone", "Repository cloned successfully!")
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Git Clone Error", f"Error cloning repository:\n{e}")
            finally:
                os.chdir(currentDir)

    def loadPlugins(self):
        self.toolsMenu.clear()  # Clear existing tools from the menu
        self.plugins = {}  # Clear the plugins dictionary

        pluginsDir = "plugins"  # Name of your plugins directory
        if not os.path.exists(pluginsDir):
            os.makedirs(pluginsDir)

        for filename in os.listdir(pluginsDir):
            if filename.endswith(".py") and not filename.startswith("__"):
                pluginPath = os.path.join(pluginsDir, filename)
                self.loadPlugin(pluginPath)

    def loadPlugin(self, pluginPath):
        pluginName = os.path.splitext(os.path.basename(pluginPath))[0]

        spec = importlib.util.spec_from_file_location(pluginName, pluginPath)
        pluginModule = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pluginModule)

        if hasattr(pluginModule, "Plugin"):
            pluginInstance = pluginModule.Plugin(self)
            self.plugins[pluginName] = pluginInstance

            action = QAction(pluginName, self)
            action.triggered.connect(lambda checked, p=pluginInstance: p.execute())
            self.toolsMenu.addAction(action)


    def loadPlugins(self):
        self.toolsMenu.clear()  # Clear existing tools from the menu
        self.plugins = {}  # Clear the plugins dictionary

        pluginsDir = "plugins"  # Name of your plugins directory
        if not os.path.exists(pluginsDir):
            os.makedirs(pluginsDir)

        for filename in os.listdir(pluginsDir):
            if filename.endswith(".py") and not filename.startswith("__"):
                pluginPath = os.path.join(pluginsDir, filename)
                self.loadPlugin(pluginPath)

    def loadPlugin(self, pluginPath):
        pluginName = os.path.splitext(os.path.basename(pluginPath))[0]

        spec = importlib.util.spec_from_file_location(pluginName, pluginPath)
        pluginModule = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pluginModule)

        if hasattr(pluginModule, "Plugin"):
            pluginInstance = pluginModule.Plugin(self)
            self.plugins[pluginName] = pluginInstance

            action = QAction(pluginName, self)
            action.triggered.connect(
                lambda checked, p=pluginInstance: p.execute()
            )
            self.toolsMenu.addAction(action)


    def updateStatusBar(self):
        currentWidget = self.tabWidget.currentWidget()
        if currentWidget:
            textEdit = currentWidget.findChild(QTextEdit)
            if textEdit:
                cursor = textEdit.textCursor()
                line = cursor.blockNumber() + 1
                col = cursor.columnNumber() + 1
                self.statusBar.showMessage(f"Line {line}, Column {col}")

    def about(self):
        QMessageBox.about(
            self,
            "About APad",
            "This is APad, a simple text editor created using PyQt5.\n\n"
            "Developed by: AlejandrixDev\n"
            "Version: 1.0"
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TextEditor()
    sys.exit(app.exec_())