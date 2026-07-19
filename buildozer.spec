[app]
title = MS 
package.name = ms
package.domain = com.kami3kaze.ms
source.include_exts = py,png,jpg,kv,atlas,bin,json,ttf
source.dir = .
requirements = python3,kivy, plyer,pillow,android
version = 1.0
requirements = python3,kivy

orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png
# صلاحيات الوصول لملفات الهاتف
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a

android.allow_backup = True
android.private_storage = False
p4a.branch = v2024.01.21

android.release_artifact = apk
android.keystore = 
android.keystore_passwd = 
android.keyalias = 
android.keyalias_passwd = 
[buildozer]
log_level = 2
warn_on_root = 1
