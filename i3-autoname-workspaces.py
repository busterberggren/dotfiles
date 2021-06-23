#!/usr/bin/env python3

# This script listens for i3 events and updates workspace names to show icons
# for running programs.  It contains icons for a few programs, but more can
# easily be added by inserting them into WINDOW_ICONS below.

import i3ipc
import subprocess as proc
import re
import signal
import sys

# Add icons here for common programs you use.  The keys are the X window class
# (WM_CLASS) names and the icons can be any text you want to display. However
# most of these are character codes for font awesome:
#   http://fortawesome.github.io/Font-Awesome/icons/
FA_CHROME = '\uf268'
FA_CODE = '\uf121'
FA_DOWNLOAD = '\uf019'
FA_FACEBOOK = '\uf09a'
FA_FILE_PDF_O = '\uf1c1'
FA_FILE_TEXT_O = '\uf0f6'
FA_FILES_O = '\uf0c5'
FA_FIREFOX = '\uf269'
FA_GAMEPAD = '\uf11b'
FA_KEY = '\uf084'
FA_MICROPHONE = '\uf130'
FA_MUSIC = '\uf001'
FA_PAINT_BRUSH = '\uf1fc'
FA_PAPER_PLANE = '\uf1d8'
FA_PICTURE_O = '\uf03e'
FA_PLAY_CIRCLE = '\uf144'
FA_PLAY_CIRCLE_O = '\uf01d'
FA_SPACE_SHUTTLE = '\uf197'
FA_SPOTIFY = '\uf1bc'
FA_STEAM = '\uf1b6'
FA_TELEGRAM = '\uf2c6'
FA_TERMINAL = '\uf120'
WINDOW_ICONS = {
    'evince': FA_FILE_PDF_O,
    'deluge': FA_DOWNLOAD,
    'feh': FA_PICTURE_O,
    'Firefox': FA_FIREFOX,
    'Firefox Beta': FA_FIREFOX,
    'FTL': FA_SPACE_SHUTTLE,
    'Gimp': FA_PAINT_BRUSH,
    'google-chrome': FA_CHROME,
    'Keepassx2': FA_KEY,
    'libreoffice': FA_FILE_TEXT_O,
    'LolClient.exe': FA_GAMEPAD,
    'messenger for desktop': FA_FACEBOOK,
    'mpv': FA_PLAY_CIRCLE,
    'Mumble': FA_MICROPHONE,
    'mupdf': FA_FILE_PDF_O,
    'MuseScore2': FA_MUSIC,
    'Nautilus': FA_FILES_O,
    'spotify': FA_MUSIC,
    'Steam': FA_STEAM,
    'subl': FA_CODE,
    'subl3': FA_CODE,
    'Telegram': FA_PAPER_PLANE,
    'TelegramDekstop': FA_PAPER_PLANE,
    'telegram-desktop': FA_PAPER_PLANE,
    'thunar': FA_FILES_O,
    'urxvt': FA_TERMINAL,
}

i3 = i3ipc.Connection()

# Returns an array of the values for the given property from xprop.  This
# requires xorg-xprop to be installed.
def xprop(win_id, property):
    try:
        prop = proc.check_output(['xprop', '-id', str(win_id), property], stderr=proc.DEVNULL)
        prop = prop.decode('utf-8')
        return re.findall('"([^"]+)"', prop)
    except proc.CalledProcessError as e:
        print("Unable to get property for window '%s'" % str(win_id))
        return None

def icon_for_window(window):
    classes = xprop(window.window, 'WM_CLASS')
    if classes != None and len(classes) > 0:
        for cls in classes:
            if cls in WINDOW_ICONS:
                return WINDOW_ICONS[cls]
        print('No icon available for window with classes: %s' % str(classes))
    return '*'

# renames all workspaces based on the windows present
def rename():
    for workspace in i3.get_tree().workspaces():
        icons = [icon_for_window(w) for w in workspace.leaves()]
        icon_str = ': ' + ''.join(icons) if len(icons) else ''
        #icon_str = ': ' + '\u0085'.join(icons) if len(icons) else ''
        #icon_str = ': '
        #for icon in icons:
        #    icon_str = icon_str + icon + ' '
        new_name = str(workspace.num) + icon_str
        print(new_name)
        i3.command('rename workspace "%s" to "%s"' % (workspace.name, new_name))

rename()

# exit gracefully when ctrl+c is pressed
def signal_handler(signal, frame):
    # rename workspaces to just numbers on exit to indicate that this script is
    # no longer running
    for workspace in i3.get_tree().workspaces():
        i3.command('rename workspace "%s" to "%d"' % (workspace.name, workspace.num))
    i3.main_quit()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# call rename() for relevant window events
def on_change(i3, e):
    if e.change in ['new', 'close', 'move']:
        rename()
i3.on('window', on_change)
i3.main()
