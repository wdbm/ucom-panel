#!/usr/bin/env python

"""
################################################################################
#                                                                              #
# UCOM-panel                                                                   #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program is a desktop environment panel.                                 #
#                                                                              #
# copyright (C) 2016 William Breaden Madden                                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

Usage:
    program [options]

Options:
    -h, --help               display help message
    --version                display version and exit
    -v, --verbose            verbose logging
    -s, --silent             silent
    -u, --username=USERNAME  username
    --foregroundcolor=COLOR  foreground color         [default: ffffff]
    --backgroundcolor=COLOR  background color         [default: 3861aa]
    --paneltext=TEXT         panel text               [default: UCOM]
    --windowframe=BOOL       include window frame     [default: false]
    --setposition=BOOL       set launcher position    [default: true]
    --screennumber=NUMBER    set launch screen number [default: -1]
"""

name    = "UCOM-panel"
version = "2016-12-22T0247Z"
logo    = None

import docopt
import logging
import os
import propyte
from PyQt4 import QtGui, QtCore
import subprocess
import shijian
import sys
import threading
import time

def main(options):

    global program
    program = propyte.Program(
        options = options,
        name    = name,
        version = version,
        logo    = logo
    )
    global log
    from propyte import log

    program.color_1        = options["--foregroundcolor"]
    program.color_2        = options["--backgroundcolor"]
    program.panel_text     = options["--paneltext"]
    program.window_frame   = options["--windowframe"].lower() == "true"
    program.set_position   = options["--setposition"].lower() == "true"
    program.screen_number  = int(options["--screennumber"])

    application = QtGui.QApplication(sys.argv)
    panel = Panel()
    panel.move(
        application.desktop().screenGeometry(program.screen_number).left(),
        application.desktop().screenGeometry(program.screen_number).top()
    )
    sys.exit(application.exec_())

class Panel(QtGui.QWidget):

    def __init__(
        self,
        ):
        super(Panel, self).__init__()

        self.text_panel = QtGui.QLabel(program.panel_text)

        self.indicator_clock = QtGui.QLabel(self)

        self.menu = QtGui.QMenu(self)
        self.menu.addAction("Openbox Configuration Manager")
        self.menu.addAction("unity-control-center")
        self.menu.addAction("close panel")
        self.menu.addAction("suspend")
        self.menu.addAction("hibernate")
        self.menu.addAction("reboot")
        self.menu.addAction("shut down")
        self.menu.triggered[QtGui.QAction].connect(self.process_menu)

        self.button_menu = QtGui.QPushButton("settings")
        self.button_menu.setMenu(self.menu)

        hbox = QtGui.QHBoxLayout()
        if program.panel_text != "":
            hbox.addWidget(self.text_panel)
        hbox.addStretch(1)
        hbox.addWidget(self.indicator_clock)
        hbox.addStretch(1)
        hbox.addWidget(self.button_menu)
        self.setLayout(hbox)

        self.setStyleSheet(
            """
            color: #{color_1};
            background-color: #{color_2}
            """.format(
                color_1 = program.color_1,
                color_2 = program.color_2
            )
        )

        self.text_panel.setStyleSheet(
            """
            QLabel{{
                color: #{color_1};
                background-color: #{color_2};
                /*
                border: 1px solid #{color_1};
                */
            }}
            """.format(
                color_1 = program.color_1,
                color_2 = program.color_2
            )
        )

        self.indicator_clock.setStyleSheet(
            """
            QLabel{{
                color: #{color_1};
                background-color: #{color_2};
                /*
                border: 1px solid #{color_1};
                */
            }}
            """.format(
                color_1 = program.color_1,
                color_2 = program.color_2
            )
        )

        self.menu.setStyleSheet(
            """
            QMenu{{
                color: #{color_1};
                background-color: #{color_2};
                /*
                border: 1px solid #{color_1};
                */
            }}
            QMenu::item{{
                color: #{color_1};
                background-color: #{color_2};
                /*
                border: 1px solid #{color_1};
                */
            }}
            QMenu::item::selected{{
                color: #{color_2};
                background-color: #{color_1};
                /*
                border: 1px solid #{color_1};
                */
            }}
            """.format(
                color_1 = program.color_1,
                color_2 = program.color_2
            )
        )

        self.button_menu.setStyleSheet(
            """
            QPushButton{{
                color: #{color_1};
                background-color: #{color_2};
                border: none;
                margin: 0px;
                padding: 0px;
            }}
            QPushButton:pressed{{
                color: #{color_1};
                background-color: #{color_2};
                border: none;
                margin: 0px;
                padding: 0px;
            }}
            """.format(
                color_1 = program.color_1,
                color_2 = program.color_2
            )
        )

        if program.window_frame is False:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        if program.set_position is True:
            self.move(0, 0)

        self.resize(QtGui.QDesktopWidget().screenGeometry().width(), 15)

        thread_clock = threading.Thread(
            target = self.clock
        )
        thread_clock.daemon = True
        thread_clock.start()

        self.show()

    def process_menu(
        self,
        action
        ):
        action_text = action.text()
        if action_text == "Openbox Configuration Manager":
            engage_command("obconf")
        if action_text == "unity-control-center":
            engage_command("unity-control-center")
        if action_text == "close panel":
            program.terminate()
        if action_text == "suspend":
            engage_command("systemctl suspend")
        if action_text == "hibernate":
            engage_command("systemctl hibernate")
        if action_text == "reboot":
            engage_command("systemctl reboot")
        if action_text == "shut down":
            engage_command("systemctl poweroff")

    def clock(
        self
        ):
        while True:
            self.indicator_clock.setText(
                shijian.time_UTC(
                    style = "YYYY-MM-DD HH:MM:SS UTC"
                )
            )
            time.sleep(1)

def engage_command(
    command = None
    ):
    process = subprocess.Popen(
        [command],
        shell      = True,
        executable = "/bin/bash")
    process.wait()
    output, errors = process.communicate()
    return output

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(programVersion)
        exit()
    main(options)
