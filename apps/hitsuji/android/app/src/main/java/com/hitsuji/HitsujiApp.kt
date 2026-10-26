package com.hitsuji

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class HitsujiApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // TODO(L1): NotificationChannel 4 段階の初期化、WorkManager 初期化
    }
}
