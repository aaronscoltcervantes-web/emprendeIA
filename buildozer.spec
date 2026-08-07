[app]

# (str) Title of your application
title = Mi Aplicacion

# (str) Package name
package.name = myapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.ejemplo

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,README.md

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# CORREGIDO: Se usa la versión estable de kivy para evitar errores en pip
requirements = python3,kivy

# (str) Custom source folders for requirements
# Sets custom source for any requirement with recipes or site-packages
#requirements.source.kivy = ../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientations (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = my service:./service.py

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the valid color names:
# 'red', 'blue', 'green', 'white', 'black', 'magenta', 'cyan', 'yellow', 'gray', 'grey', 'lightgray', 'lightgrey', 'darkgray', 'darkgrey'
#android.presplash_color = red

# (list) Permissions
#android.permissions = INTERNET

# (list) features (e.g. android.hardware.camera)
#android.features = android.hardware.camera

# (int) Target Android API, should be as high as possible.
#android.api = 33

# (int) Minimum API your APK / AAB will support.
#android.minapi = 21

# (str) Android NDK version to use
#android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This should be True, if you don't want to update for each build!
#android.skip_update = False

# (bool) If True, then accept all the licenses automatically of android tools
#android.accept_sdk_license = False

# (list) Android application architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Enable AndroidX support. Required when aiming android.api >= 28
android.enable_androidx = True

#
# Python for android (p4a) specific
#

# (str) python-for-android git clone directory (if empty, it will be cloned)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for custom recipes
#p4a.local_recipes =

# (str) A bootstrap to use, e.g. --bootstrap=sdl2
#p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= (default is 5000)
#p4a.port =


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable, 1 = enable)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (APK, AAB, etc.) storage
# bin_dir = ./bin
