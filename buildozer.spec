[app]

# (str) Title of your application
title = Mi Aplicacion

# (str) Package name
package.name = myapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.ejemplo

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 0.1

# ── FIX: versión de kivy estable con wheels disponibles ──
requirements = python3, kivy==2.3.0

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

#
# Android specific
#

# (bool) Accept licenses automatically
android.accept_sdk_license = True

# (str) Android NDK version
android.ndk = 25b

# (int) Target Android API and Build-Tools version
android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.2

# (list) Android application architectures
android.archs = arm64-v8a

# (bool) Enable AndroidX support
android.enable_androidx = True

# ── FIX: forzar Python 3.11 (compatible con kivy==2.3.0) ──
p4a.python_version = 3.11

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off)
warn_on_root = 0
