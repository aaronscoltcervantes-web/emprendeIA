[app]
title = MiAppEmprende
package.name = emprendeia
package.domain = org.emprendeia
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# OBLIGATORIO: Incluir hostpython3 para que Kivy se compile desde código fuente
requirements = python3,kivy,hostpython3

version = 0.1
android.permissions = INTERNET

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
