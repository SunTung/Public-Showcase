plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }
android {
    namespace = "tw.suntung.pocketrecorder"
    compileSdk = 36
    defaultConfig {
        applicationId = "tw.suntung.pocketrecorder"
        minSdk = 26
        targetSdk = 36
        versionCode = 2
        versionName = "1.2.0"
    }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}

dependencies {
    implementation("com.google.android.gms:play-services-ads:25.5.0")
    implementation("com.google.android.ump:user-messaging-platform:4.0.0")
}
