[app]

title = Registro Óptica
package.name = registrooptica
package.domain = org.optica

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = bin,.buildozer,.git,.github,__pycache__

version = 0.1

requirements = python3==3.11.5,hostpython3==3.11.5,kivy==2.3.0,kivymd==1.2.0,pillow,plyer,pyjnius,android

orientation = portrait
fullscreen = 0

# Permisos (en API 33 el almacenamiento externo clásico ya no aplica)
android.permissions = CAMERA

# Android
android.api = 33
android.minapi = 24
android.ndk = 25b
android.build_tools_version = 33.0.2
android.archs = arm64-v8a
android.enable_androidx = True
android.accept_sdk_license = True

# Filtro de logcat para depurar
android.logcat_filters = *:S python:D

# python-for-android fijo para builds reproducibles
p4a.branch = v2024.01.21

[buildozer]

log_level = 2
warn_on_root = 0
