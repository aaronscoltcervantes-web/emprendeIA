[app]
title = MiAppEmprende
package.name = emprendeia
package.domain = org.emprendeia
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# QUITAR sqlite3 DE ESTA LÍNEA (ya viene incluido en python3):
requirements = python3,kivy

version = 0.1
android.permissions = INTERNET

# Configuración recomendada para NDK/API en GitHub Actions:
android.api = 33
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 33.0.2
android.accept_sdk_license = True

android.private = True
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
