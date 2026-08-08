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

# (list) Application requirements (usando python3.11 compatible)
requirements = python3.11, https://github.com/kivy/kivy/archive/refs/tags/2.3.0.zip

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
android.archs = arm64-v8a, armeabi-v7a

# (bool) Enable AndroidX support
android.enable_androidx = True


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off)
warn_on_root = 0
