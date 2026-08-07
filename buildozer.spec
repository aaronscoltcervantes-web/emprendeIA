[app]
title = MiAppEmprende
package.name = emprendeia
package.domain = org.emprendeia
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# CORRECCIÓN 1: Agregar sqlite3 explícitamente
requirements = python3,kivy==master,sqlite3

version = 0.1

# CORRECCIÓN 2: Agregar permisos de lectura/escritura para la base de datos
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 33.0.2
android.accept_sdk_license = True

android.private = True

# CORRECCIÓN 3: Agregar arquitectura de 32 bits por compatibilidad
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
