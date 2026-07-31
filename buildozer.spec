[app]
title = FarmaNoah
package.name = farmanoah
package.domain = org.farmanoah
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
version = 1.0

# 1. Removido 'cython' de los requirements
requirements = python3,kivy

orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.accept_sdk_license = True
android.api = 33
android.min_api = 21
android.sdk = 33
android.ndk = 25b

# AGREGAR ESTA LÍNEA AQUÍ:
android.archs = arm64-v8a

# 2. Desactivadas las versiones inestables de p4a
# p4a.branch = master
# p4a.python_version = 3.11

[buildozer]
log_level = 2
warn_on_root = 1
