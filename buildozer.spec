[app]

# (str) Android build-tools version to use
android.build_tools_version = 33.0.2
# (str) Title of your application
title = MiAppEmprende

# (str) Package name
package.name = emprendeia

# (str) Package domain (needed for android/ios packaging)
package.domain = org.emprendeia

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# IMPORTANTE: Dejar 'kivy' sin fijar versión y fijar cython < 3.0.0
requirements = python3,kivy,hostpython3

# (str) Custom source folders for requirements
# version of your application
version = 0.1

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private = True

# (list) List of accept structures (archs)
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 1
