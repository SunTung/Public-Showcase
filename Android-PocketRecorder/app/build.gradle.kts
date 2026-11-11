plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }
val productionAppId = "ca-app-pub-1343937669240075~7835518057"
val productionBannerId = "ca-app-pub-1343937669240075/3821085574"
val testAppId = "ca-app-pub-3940256099942544~3347511713"
val testBannerId = "ca-app-pub-3940256099942544/9214589741"

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
    buildTypes {
        getByName("debug") {
            manifestPlaceholders["admobAppId"] = testAppId
            buildConfigField("String", "BANNER_AD_UNIT_ID", "\\"" + testBannerId + "\\"")
            buildConfigField("boolean", "USES_LIVE_ADS", "false")
        }
        getByName("release") {
            manifestPlaceholders["admobAppId"] = productionAppId
            buildConfigField("String", "BANNER_AD_UNIT_ID", "\\"" + productionBannerId + "\\"")
            buildConfigField("boolean", "USES_LIVE_ADS", "true")
        }
    }
    buildFeatures { buildConfig = true }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}

dependencies {
    implementation("com.google.android.gms:play-services-ads:25.5.0")
    implementation("com.google.android.ump:user-messaging-platform:4.0.0")
}
