# -*- coding: utf-8 -*-

"""
***************************************************************************
    BatchInputSelectionPanel.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
from PyQt4 import QtGui, QtCore
from processing.parameters.ParameterMultipleInput import ParameterMultipleInput
from processing.gui.MultipleInputDialog import MultipleInputDialog
from processing.tools import dataobjects
from processing.parameters.ParameterRaster import ParameterRaster
from processing.parameters.ParameterVector import ParameterVector
from processing.parameters.ParameterTable import ParameterTable


class BatchInputSelectionPanel(QtGui.QWidget):

    def __init__(self, param, row, col, batchDialog, parent=None):
        super(BatchInputSelectionPanel, self).__init__(parent)
        self.param = param
        self.batchDialog = batchDialog
        self.table = batchDialog.table
        self.row = row
        self.col = col
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.text = QtGui.QLineEdit()
        self.text.setText('')
        self.text.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                QtGui.QSizePolicy.Expanding)
        self.horizontalLayout.addWidget(self.text)
        self.pushButton = QtGui.QPushButton()
        self.pushButton.setText('...')
        self.pushButton.clicked.connect(self.showPopupMenu)
        self.horizontalLayout.addWidget(self.pushButton)
        self.setLayout(self.horizontalLayout)

    def showPopupMenu(self):
        popupmenu = QtGui.QMenu()
        if not (isinstance(self.param, ParameterMultipleInput)
                    and self.param.datatype == ParameterMultipleInput.TYPE_FILE):
            selectLayerAction = QtGui.QAction('Select from open layers',
                self.pushButton)
            selectLayerAction.triggered.connect(self.showLayerSelectionDialog)
            popupmenu.addAction(selectLayerAction)
        selectFileAction = QtGui.QAction('Select from filesystem',
                self.pushButton)
        selectFileAction.triggered.connect(self.showFileSelectionDialog)
        popupmenu.addAction(selectFileAction)
        popupmenu.exec_(QtGui.QCursor.pos())

    def showLayerSelectionDialog(self):
        if (isinstance(self.param, ParameterRaster)
                or (isinstance(self.param, ParameterMultipleInput)
                    and self.param.datatype == ParameterMultipleInput.TYPE_RASTER)):
            layers = dataobjects.getRasterLayers()
        elif isinstance(self.param, ParameterTable):
            layers = dataobjects.getTables()
        else:
            if isinstance(self.param, ParameterVector):
                datatype = self.param.shapetype
            else:
                datatype = [self.param.datatype]
            layers = dataobjects.getVectorLayers(datatype)
        dlg = MultipleInputDialog([layer.name() for layer in layers])
        dlg.exec_()
        if dlg.selectedoptions is not None:
            selected = dlg.selectedoptions
            if len(selected) == 1:
                self.text.setText(layers[selected[0]])
            else:
                if isinstance(self.param, ParameterMultipleInput):
                    self.text.setText(';'.join(layers[idx].name() for idx in selected))
                else:
                    rowdif = len(layers) - (self.table.rowCount() - self.row)
                    for i in range(rowdif):
                        self.batchDialog.addRow()
                    for i, layeridx in enumerate(selected):
                        self.table.cellWidget(i + self.row,
                                self.col).setText(layers[layeridx].name())

    def showFileSelectionDialog(self):
        settings = QtCore.QSettings()
        text = unicode(self.text.text())
        if os.path.isdir(text):
            path = text
        elif os.path.isdir(os.path.dirname(text)):
            path = os.path.dirname(text)
        elif settings.contains('/Processing/LastInputPath'):
            path = unicode(settings.value('/Processing/LastInputPath'))
        else:
            path = ''

        ret = QtGui.QFileDialog.getOpenFileNames(self, 'Open file', path,
                self.param.getFileFilter())
        if ret:
            files = list(ret)
            if len(files) == 1:
                settings.setValue('/Processing/LastInputPath',
                                  os.path.dirname(unicode(files[0])))
                self.text.setText(files[0])
            else:
                settings.setValue('/Processing/LastInputPath',
                                  os.path.dirname(unicode(files[0])))
                if isinstance(self.param, ParameterMultipleInput):
                    self.text.setText(';'.join(unicode(f) for f in files))
                else:
                    rowdif = len(files) - (self.table.rowCount() - self.row)
                    for i in range(rowdif):
                        self.batchDialog.addRow()
                    for i, f in enumerate(files):
                        self.table.cellWidget(i + self.row,
                                self.col).setText(f)

    def setText(self, text):
        return self.text.setText(text)

    def getText(self):
        return self.text.text()
