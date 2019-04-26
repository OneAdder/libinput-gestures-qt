'''libinput-gestures-qt. User interface for the libinput-gestures utility. 
    Copyright (C) 2019  Michael Voronov

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
"""
This is a GUI for libinout-gestures-utility. Allows to set up touchpad gestures:
allows to edit the configuration file and control utility status.

Variables:
--------------
Paths:
-----
HOME: str
    path to user's home directory
CONFIG_LOCATION: str
    path to the location of the configuration file
LOGO_LOCATION: str
    path to logo
Mappings:
--------
actions_mapping: dict
    finger actions in human-readable form >> finger actions in config-readable form
reversed_mapping: dict
    finger actions in config-readable form >> finger actions in human-readable form
keys_mapping: dict
    qt keys (lowered) >> xdotool keys
Other:
-----
kde_defaults: str
    Default settings for KDE Plasma
kde_defaults_description: str
    Descriptin for KDE defaults.
copyleft: str
    Copyleft note.
--------------
Classes:
GesturesApp(QtWidgets.QMainWindow, main_window.Ui_MainWindow)
    Main window.
EditGestures(QtWidgets.QWidget, edit_window.Ui_Form)
    Secondary window for adding/editing gestures.
--------------
Functions: read_config, write_config, find_key_combo, getqdbus_name, main
--------------
"""

import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from libinput_gestures_qt import main_window
from libinput_gestures_qt import edit_window

import subprocess
from pathlib import Path
import os

import re

HOME = str(Path.home())
CONFIG_LOCATION = HOME + '/.config/libinput-gestures.conf'
LOGO_LOCATION = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'logo' + os.path.sep + 'libinput-gestures-qt.png'

actions_mapping = {
    'Swipe Up': 'gesture swipe up',
    'Swipe Down': 'gesture swipe down',
    'Swipe Left': 'gesture swipe left',
    'Swipe LeftUp': 'gesture swipe left_up',
    'Swipe LeftDown': 'gesture swipe  left_down',
    'Swipe Right': 'gesture swipe right',
    'Swipe RightUp': 'gesture swipe right_up',
    'Swipe RightDown': 'gesture swipe right_down',
    'Pinch In': 'gesture pinch in',
    'Pinch Out': 'gesture pinch out',
    'Pinch Clockwise': 'gesture pinch clockwise',
    'Pinch Anticlockwise': 'gesture pinch anticlockwise',
}

reversed_mapping = {
    'gesture swipe up': 'Swipe Up',
    'gesture swipe down': 'Swipe Down',
    'gesture swipe left': 'Swipe Left',
    'gesture swipe left_up': 'Swipe LeftUp',
    'gesture swipe left_down': 'Swipe LeftDown',
    'gesture swipe right': 'Swipe Right',
    'gesture swipe right_up': 'Swipe RightUp',
    'gesture swipe right_down': 'Swipe RightDown',
    'gesture pinch in': 'Pinch In',
    'gesture pinch out': 'Pinch Out',
    'gesture pinch clockwise': 'Pinch Clockwise',
    'gesture pinch anticlockwise': 'Pinch Anticlockwise'
}

keys_mapping = {
    'meta': 'super',
    'pgdown': 'Page_Down',
    'pgup': 'Page_Up',
    'right': 'Right',
    'left': 'Left',
    'up': 'Up',
    'down': 'Down',
    'f1': 'F1',
    'f2': 'F2',
    'f3': 'F3',
    'f4': 'F4',
    'f5': 'F5',
    'f6': 'F6',
    'f7': 'F7',
    'f8': 'F8',
    'f9': 'F9',
    'f10': 'F10',
    'f11': 'F11',
    'f12': 'F12',
}

kde_defaults = '''
#This default settings for KDE Plasma generated by libinput-gestures-qt
#
#Browser actions Back and Forward
gesture swipe left 3 xdotool key alt+Right
gesture swipe right 3 xdotool key alt+Left
#
#Present Windows
gesture swipe down 3 {qdbus} org.kde.kglobalaccel /component/kwin invokeShortcut "Expose"
#
#Desktop Grid
gesture swipe up 3  {qdbus} org.kde.kglobalaccel /component/kwin invokeShortcut "ShowDesktopGrid"
#
#Minimize
gesture swipe down 4 {qdbus} org.kde.kglobalaccel /component/kwin invokeShortcut "Window Minimize"
#
#Maximize
gesture swipe up 4 {qdbus} org.kde.kglobalaccel /component/kwin invokeShortcut "Window Maximize"
#
#Next virtual desktop
gesture swipe left 4 {qdbus} org.kde.kglobalaccel /component/kwin invokeShortcut "Switch to Next Desktop"
#Previous virtual desktop
gesture swipe right 4 {qdbus} org.kde.kglobalaccel /component/kwin invokeShortcut "Switch to Previous Desktop"
'''

kde_defaults_description = '''
Present windows: Swipe Down (3 fingers)
Desktop Grid: Swipe Up (3 fingers)
Maximize: Swipe Up (4 fingers)
Minimize: Swipe Down (4 fingers)
Next virtual desktop: Swipe Left (4 fingers)
Previous virtual desktop: Swipe Right (4 fingers)
Browser 'Back': Swipe Right (3 fingers)
Browser 'Forward': Swipe Left (3 fingers)
'''

copyleft = '''
libinput-gestures-qt
Copyright (C) 2019  Michael Voronov
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
'''

def read_config():
    """Reads config file by lines
    
    Config under CONFIG_LOCATION = ~/.config/libinput-gestures.conf
    Returns '' if there is no config file.
    """
    try:
        with open(CONFIG_LOCATION, 'r') as config:
            conf = config.readlines()
        return conf
    except FileNotFoundError:
        return ''


def write_config(new_conf):
    """Writes config under CONFIG_LOCATION
    
    Parameter: new_conf, list of strings
    """
    with open(CONFIG_LOCATION, 'w') as config:
        config.write(''.join(new_conf))

def write_defaults(defaults):
    """Write default settings and backs old config up

    Returns defaults
    """
    old_conf = read_config()
    with open(CONFIG_LOCATION + '.old', 'w') as config:
        config.write(''.join(old_conf))
    with open(CONFIG_LOCATION, 'w') as config:
        config.write(defaults)
    return defaults

def fix_config():
    """Fixes config
    
    Reads config, goes by lines.
    If lise starts with '#', it is preserved.
    If line starts with 'gesture', 'device' or 'swipe_threshold'
        and this line is ok, it is preserved.
    Other lines are deleted.
    """
    conf = read_config()
    fixed_conf = []
    for line in conf:
        if line.startswith('#') or line == '\n':
            fixed_conf.append(line)
        else:
            splitted = line.replace('\t', ' ').split()
            if splitted[0] in ['gesture', 'device', 'swipe_threshold']:
                if splitted[0] == 'gesture':
                    if splitted[4] == 'xdotool':
                        if splitted[5] == 'key' and len(splitted) == 7:
                            fixed_conf.append(line)
                    elif 'qdbus' in splitted[4]:
                        if splitted[-1].endswith('"'):
                            fixed_conf.append(line)
                    else:
                        fixed_conf.append(line)
                else:
                    if len(splitted) == 2:
                            fixed_conf.append(line)
    write_config(''.join(fixed_conf))

def resub_config():
    """Delete multiple tabs and spaces"""
    conf = ''.join(read_config())
    conf = re.sub('(\t)+', ' ', conf)
    conf = re.sub('\t', ' ', conf)
    conf = re.sub('( )+', ' ', conf)
    write_config(conf)


def find_key_combo(qt_key_combo):
    """Key combo translator
    
    Takes string with QT-like key combo (generated by PyQt5.QtWidgets.QKeySequenceEdit)
    mapes into a string consumable by xdotool
    """
    xdotool_key_combo = []
    for qt_key in qt_key_combo.split('+'):
        lowered_key = qt_key.lower()
        if lowered_key in keys_mapping:
            xdotool_key_combo.append(keys_mapping[lowered_key])
        else:
            xdotool_key_combo.append(lowered_key)
    return '+'.join(xdotool_key_combo)

def get_qdbus_name():
    """It's either 'qdbus' or 'qdbus-qt5'"""
    try:
        subprocess.run('qdbus', capture_output=True)
        return 'qdbus'
    except FileNotFoundError:
        subprocess.run('qdbus-qt5', capture_output=True)
        return 'qdbus-qt5'


class GesturesApp(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    """Main window.
    
    Display current configuration, menubar and the 'Add' button.
    """
    def __init__(self, parent=None):
        """init
        
        Calls for self.display_config() and adds triggers to all the events.
        Resubs config (multiple tabs and spaces)
        Tries to launch libinput-gestures-setup:
            if it works, sets self.installed to True
            if not sets self.installed to False
        """
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Libinput Gestures Qt')
        self.setWindowTitle('Add Gestures')
        self.setWindowIcon(QtGui.QIcon(LOGO_LOCATION))
        self.QDBUS_NAME = get_qdbus_name()
        if not self.QDBUS_NAME:
            reply = QtWidgets.QMessageBox.question(self, "Cannot find qdbus",
                                                   'Unable to find qdbus binary.\n'
                                                   'It is a utility included into KDE Plasma used by this app.\n'
                                                   'If you have qdbus but it is called somewhat else, alias it to "qdbus" and restart the app.\n'
                                                   'If not, you will not be able to use KDE defaults and map Plasma actions.'
                                                   'Continue?',
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                   QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.No:
                sys.exit()

        self.kde_defaults = kde_defaults.format(qdbus=self.QDBUS_NAME)
        
        resub_config()
        self.display_config()

        self.pushButton.clicked.connect(self.start_adding)

        #Menubar actions <--
        #File
        self.actionRefresh.triggered.connect(self.refresh)
        self.actionSet_to_default_KDE.triggered.connect(self.set_KDE_default)
        self.actionImport_config_file.triggered.connect(self.import_config)
        
        #Service
        self.actionStatus.triggered.connect(self.display_status)
        self.actionRestart.triggered.connect(self.restart_utility)
        self.actionStop.triggered.connect(self.stop_utility)
        self.actionStart.triggered.connect(self.start_utility)
        
        #About
        self.actionDefaults_KDE_Plasma.triggered.connect(self.show_kde_defaults)
        self.actionLicense.triggered.connect(self.show_copyleft)
        #-->
        try:
            subprocess.run(['libinput-gestures-setup', 'status'], capture_output=True)
            self.installed = True
        except FileNotFoundError:
            QtWidgets.QMessageBox.about(self, "Problem", "Cannot find libinput-gestures. Are you sure it is installed correctly?")
            self.installed = False


    def start_adding(self):
        """Shows EditGestures window"""
        self.adding = EditGestures(self)
        self.adding.setWindowModality(QtCore.Qt.WindowModal)
        self.adding.show()

    '''
    File Menu
    _____________________________________________________________________________________________
    '''
    def refresh(self):
        """Refresh content of the main window"""
        self.display_config(refresh=True)

    def set_KDE_default(self):
        """Set default settings for KDE Plasma"""
        reply = QtWidgets.QMessageBox.question(
            self, 'Message',
            'Set to defaults?\n'
            'Configuration file will be backed up.\n'
            'You will be able to import it from ~/.cofig/libinput-gestures.conf.old',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            if self.QDBUS_NAME:
                write_defaults(self.kde_defaults)
                self.display_config(refresh=True)
            else:
                QtWidgets.QMessageBox.about(self, 'No qdbus', 'You cannot do it without qdbus:(')

    def import_config(self):
        """Import some config file"""
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Import', HOME)
        #Without this try-except the app krashes when I close the Import window
        try:
            with open(fname[0]) as f:
                imported_config = f.readlines()
            write_config(imported_config)
            resub_config()
            fix_config()
            self.display_config(refresh=True)
        except FileNotFoundError:
            pass
        

    '''
    Service Menu
    _____________________________________________________________________________________________
    '''
    def display_status(self):
        """Check status of libinput-gestures and shows it in message box"""
        if self.installed:
            status = subprocess.run(['libinput-gestures-setup', 'status'], capture_output=True)
            status = status.stdout.decode('utf-8')
            installed = 'no'
            if 'is installed' in status:
                installed = 'yes'
            running = 'no'
            if 'is running' in status:
                running = 'yes'
            set_to_autostart = 'no'
            if 'is set to autostart' in status:
                set_to_autostart = 'yes'
            status = 'Installed: {}\nRunning: {}\nAutostart: {}\n'.format(installed, running, set_to_autostart)
            QtWidgets.QMessageBox.about(self, "Status", status)
    
    def restart_utility(self):
        """Runs 'libinput-gestures-setup restart', displays output in message box"""
        if self.installed:
            status = subprocess.run(['libinput-gestures-setup', 'restart'], capture_output=True)
            status = status.stdout.decode('utf-8')
            QtWidgets.QMessageBox.about(self, "Status", status)
    
    def stop_utility(self):
        """Runs 'libinput-gestures-setup stop', displays output in message box"""
        if self.installed:
            status = subprocess.run(['libinput-gestures-setup', 'stop'], capture_output=True)
            status = status.stdout.decode('utf-8')
            QtWidgets.QMessageBox.about(self, "Status", status)
    
    def start_utility(self):
        """Runs 'libinput-gestures-setup start', displays output in message box"""
        if self.installed:
            status = subprocess.run(['libinput-gestures-setup', 'start'], capture_output=True)
            status = status.stdout.decode('utf-8')
            QtWidgets.QMessageBox.about(self, "Status", status)

    '''
    About Menu
    _____________________________________________________________________________________________
    '''
    def show_kde_defaults(self):
        """Show info about KDE defaults"""
        QtWidgets.QMessageBox.about(self, "KDE Plasma Defaults", kde_defaults_description)

    def show_copyleft(self):
        """Show copyleft note"""
        QtWidgets.QMessageBox.about(self, "KDE Plasma Defaults", copyleft)

    '''
    Getting config to display handsomely
    _____________________________________________________________________________________________
    '''
    def sort_config(self):
        """Sorts config contents alphabetically.
        
        Assigns new values for:
            self.gestures: list of str
                finger actions in human-readable form
                e.g. ['Swipe Up']
            self.fingers: list of int
                amount of fingers
                e.g. [3]
            self.shortcuts: list of str
                keyboard shortcuts (in the xdotool form)
                OR commands
                e.g. ['ctrl+super+Page_Down']
                e.g. ['echo "Hello"']
            self.buttons: list of str
                e.g. ['gesture swipe up 3']
            self.actions: list of str
                either 'shortcut' (stands for a keyboard shortcut)
                or 'command'
        """
        for_sorting = []
        for i, el in enumerate(self.gestures):
            for_sorting.append([el, (self.fingers[i], self.shortcuts[i], self.buttons[i], self.actions[i])])
        sorted_conf = sorted(for_sorting)
        
        self.gestures = []
        self.fingers = []
        self.shortcuts = []
        self.buttons = []
        self.actions = []
        for line in sorted_conf:
            self.gestures.append(line[0])
            self.fingers.append(line[1][0])
            self.shortcuts.append(line[1][1])
            self.buttons.append(line[1][2])
            self.actions.append(line[1][3])
    
    def prepare_config_for_displaying(self):
        """Creates widgets for all stuff read from config
        
        Assigns new values for:                                                         V-----------------------------------V
            self.gestures: list of str                   <============ Translated from 'gesture <type:swipe|pinch> <direction> ...'
                finger actions in human-readable form
                e.g. ['Swipe Up']                                                                       V-------V
            self.fingers: list of int                    <============ Exact values of  '... <direction> <fingers> <command>...'
                amount of fingers
                e.g. [3]                                                                               V-------V
            self.shortcuts: list of str                  <======------ Exact values of  '... <fingers> <command>'
                keyboard shortcuts (in the xdotool form)        \ <<or>>                                           V-----------------V
                OR commands                                      ----- Exact values of  '... <fingers> xdotool key <keyboard_shortcut>
                e.g. ['ctrl+super+Page_Down']                     \ <<or>>                                                      V--------V
                e.g. ['echo "Hello"']                              --- Exact values of  '... <fingers> <qdbus trigger shortcut> <shortcut>' 
                
                                                                                         V------------------------------------V
            self.buttons: list of str                    <============ Exact values of  'gesture <type:swipe|pinch> <direction> ...'
                e.g. ['gesture swipe up 3']
            self.actions: list of str                    <============ Depend on whether xdotool or qdbus is used in config line
                either 'Keyboard shortcut'
                or 'Plasma action'
                or 'Command'
        """
        conf = read_config()
        self.gestures = []
        self.fingers = []
        self.shortcuts = []
        self.buttons = []
        self.actions = []
        for line in conf:
            if line.startswith('gesture'):
                splitted = line.split()
                self.gestures.append(reversed_mapping['{} {} {}'.format(splitted[0], splitted[1], splitted[2])])
                self.fingers.append(splitted[3])
                if splitted[4] == 'xdotool' and splitted[5] == 'key':
                    self.actions.append('Keyboard shortcut')
                    self.shortcuts.append(splitted[6])
                elif 'qdbus' in splitted[4]:
                    self.actions.append('Plasma action')
                    plasma_action = re.findall('"(.*?)"', line)[0]
                    if plasma_action:
                        self.shortcuts.append(plasma_action)
                    else:
                        self.shortcuts.append(splitted[-1].replace('"', ''))
                else:
                    self.actions.append('Command')
                    self.shortcuts.append(' '.join(splitted[4:]))
                self.buttons.append('{} {} {} {}'.format(splitted[0], splitted[1], splitted[2], splitted[3]))

    def display_config(self, refresh=False):
        """Displays current configuration in main window
        
        Finally gathers all widgets (creates a couple new) and puts them into nice layouts.
        """
        if refresh:
            self.area.deleteLater()
        
        try:
            self.prepare_config_for_displaying()
        except Exception:
            reply = QtWidgets.QMessageBox.question(
                self, 'Problem',
                "Something is wrong with the configuration file...\nFix it?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                fix_config()
                self.prepare_config_for_displaying()
            else:
                sys.exit()

        self.sort_config()
        
        self.layout = self.verticalLayout
        self.area = QtWidgets.QScrollArea()
        content_widget = QtWidgets.QWidget()
        self.area.setWidget(content_widget)
        flay = QtWidgets.QGridLayout(content_widget)
        self.area.setWidgetResizable(True)

        for i, label in enumerate(self.gestures):
            flay.addWidget(QtWidgets.QLabel(label), i, 0)

        for i, label in enumerate(self.fingers):
            flay.addWidget(QtWidgets.QLabel(label), i, 1)

        for i, label in enumerate(self.actions):
            flay.addWidget(QtWidgets.QLabel(label), i, 2)

        for i, label in enumerate(self.shortcuts):
            flay.addWidget(QtWidgets.QLabel(label), i, 3)

        for i, button in enumerate(self.buttons):
            deleteButton = QtWidgets.QPushButton("Delete")
            deleteButton.setAccessibleName(button)
            deleteButton.clicked.connect(self.delete_entry)
            flay.addWidget(deleteButton, i, 4)

        self.layout.addWidget(self.area)

    '''
    Delete Buttons
    _____________________________________________________________________________________________

    '''
    def delete_entry(self):
        """Delete line from config
        
        Triggered by 'Delete' buttons.
        """
        button = self.sender()
        if isinstance(button, QtWidgets.QPushButton):
            reply = QtWidgets.QMessageBox.question(
                self, 'Message',
                "Are you sure to delete?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                conf = read_config()
                new_conf = []
                for line in conf:
                    if not line.startswith(button.accessibleName()):
                        new_conf.append(line)
                write_config(new_conf)
                self.display_config(refresh=True)
        
        
class EditGestures(QtWidgets.QWidget, edit_window.Ui_Form):
    """Secondary window for adding/editing gestures
    
    Child to main window (GesturesApp).
    """
    def __init__(self, parent):
        """init
        
        Sets widgets and their attributes that I could not set in QT Designer.
        Adds events to buttons. Checks for qdbus.
        """
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.setWindowTitle('Add Gestures')
        self.setWindowIcon(QtGui.QIcon(LOGO_LOCATION))
        
        self.QDBUS_NAME = get_qdbus_name()

        self.action = 'gesture swipe up'
        self.fingers = 3
        self.shortcut = ''
        
        self.fingersLine.setMinimum(3)

        self.draw_shortcut()
        self.shortcut_command.activated[str].connect(self.shortcut_command_or_qdbus)
        
        self.actionMenu.activated[str].connect(self.action_chosen)
        self.fingersLine.valueChanged[int].connect(self.fingers_chosen)
        
        self.saveButton.clicked.connect(self.save_changes)

    def shortcut_command_or_qdbus(self, text):
        """Chose whether you want to add plain command, xdotool command using QKeySequenceEdit or qdbus command
        
        Does not delete previous widgets: they are stored one upon another.
        HELP NEEDED -- it works but it's stupid :(
        """
        if text == 'Keyboard Shortcut':
            self.draw_shortcut()
        elif text == 'Plasma action':
            if self.QDBUS_NAME:
                self.draw_plasma_actions()
        else:
            self.draw_command()

    def draw_shortcut(self):
        """Draws keyboard shortcut input
        
        ... so that user could just press buttons (sh|h)e wants
        istead of manually typing 'xdotool key <key combo>' and remember differences between xdotool/Gnome/KDE/etc.
        """
        self.shortcut = ''
        self.actionType.setText('Keyboard Shortcut')
        self.keyboardLine = QtWidgets.QKeySequenceEdit()
        self.gridLayout.addWidget(self.keyboardLine, 4, 2)
        self.keyboardLine.keySequenceChanged.connect(self.shortcut_chosen)

    def draw_plasma_actions(self):
        """Draws Plasma actions combobox input
        
        ... so that user could just choose action for Plasma
        """
        self.shortcut = self.QDBUS_NAME + ' org.kde.kglobalaccel /component/kwin invokeShortcut "Expose"'
        
        self.actionType.setText('Plasma action')
        self.plasmaActions = QtWidgets.QComboBox()
        kwin_shortcuts = subprocess.run(
            [
                self.QDBUS_NAME, 'org.kde.kglobalaccel', '/component/kwin',
                'org.kde.kglobalaccel.Component.shortcutNames'
            ],
            capture_output=True,
        )
        kwin_shortcuts = kwin_shortcuts.stdout.decode('utf-8').split('\n')[:-2]
        kwin_shortcuts.sort()
        for kwin_shortcut in kwin_shortcuts:
            self.plasmaActions.addItem(kwin_shortcut)
        self.gridLayout.addWidget(self.plasmaActions, 4, 2)
        
        self.plasmaActions.activated[str].connect(self.plasma_action_chosen)
        
    def draw_command(self):
        """Draws command input
        
        ... because I don't want users to be stuck with xdotool and qdbus
        """
        self.shortcut = ''
        self.actionType.setText('Command')
        self.commandLine = QtWidgets.QLineEdit()
        self.gridLayout.addWidget(self.commandLine, 4, 2)
        self.commandLine.textChanged[str].connect(self.command_chosen)

    def action_chosen(self, text):
        """Event when fingers action is chosen"""
        if 'Pinch' in text:
            self.fingersLine.setMinimum(2)
            self.fingersLine.setValue(2)
        else:
            self.fingersLine.setMinimum(3)
            self.fingersLine.setValue(3)
        self.action = actions_mapping[text]

    def fingers_chosen(self, value):
        """Event when amount of fingers is chosen"""
        self.fingers = value

    def shortcut_chosen(self, text):
        """Event when keyboard shortcut is chosen"""
        shortcut = text.toString().split(',')[0]
        self.shortcut = 'xdotool key ' + find_key_combo(shortcut)

    def command_chosen(self, text):
        """Event when command is typed in"""
        self.shortcut = text

    def plasma_action_chosen(self, text):
        self.shortcut = '{qdbus} org.kde.kglobalaccel /component/kwin invokeShortcut "{sh}"'.format(qdbus=self.QDBUS_NAME, sh=text)

    def save_changes(self):
        """Writes input data into config file"""
        if self.action and self.fingers and self.shortcut:
            conf = read_config()
            new_conf = []
            for line in conf:
                if not line.startswith('{} {}'.format(self.action, str(self.fingers))):
                    new_conf.append(line)
            new_conf.append('{} {} {}\n'.format(self.action, str(self.fingers), self.shortcut))
            write_config(new_conf)
            self.actionMenu.setCurrentIndex(0)
            self.fingersLine.setValue(0)
            QtWidgets.QMessageBox.about(self, "Success", "Cofiguration successfully edited.")
            self.parent.display_config(refresh=True)
            self.close()
        else:
            QtWidgets.QMessageBox.about(self, "Fail", "Please, fill all the forms.")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = GesturesApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
