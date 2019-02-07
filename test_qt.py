# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 14:27:10 2019

@author: Samuel
"""

from PyQt5 import QtWidgets, QtCore


class MyWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MyWidget, self).__init__(parent)
        self.lay = QtWidgets.QHBoxLayout() # QVBoxLqyout, # QGridLayout
        self.setLayout(self.lay)
        self.button = QtWidgets.QPushButton("Coucou", parent=self)
        self.button2 = QtWidgets.QPushButton("Coucou2", parent=self)
        self.lay.addWidget(self.button)
        self.lay.addWidget(self.button2)
        
        self.button.clicked.connect(self.do_something)
        
    def do_something(self):
        print("button clicked")
    
        


w = MyWidget()
w.show()