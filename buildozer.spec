[app]
title = مدير الملفات
package.name = filemanager
package.domain = org.example

source.dir = .
source.include_exts = py,kv,png,jpg,atlas

version = 1.0
requirements = python3,kivy

orientation = portrait
fullscreen = 0

# صلاحيات الوصول لملفات الهاتف
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
