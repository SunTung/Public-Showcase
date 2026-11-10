plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }
val prodAppId = providers.gradleProperty("ADMOB_APP_ID").orElse(System.getenv("ADMOB_APP_ID") ?: "").get()
val liveAds = Regex("^ca-app-pub-1343937669240075~[0-9]{10}$").matches(prodAppId)
val appId = if (liveAds) prodAppId else "ca-app-pub-3940256099942544~3347511713"
val bannerId = if (liveAds) "ca-app-pub-1343937669240075/3821085574" else "ca-app-pub-3940256099942544/9214589741"

android {
    namespace = "tw.suntung.pocketrecorder"
    compileSdk = 36
    defaultConfig {
        applicationId = "tw.suntung.pocketrecorder"
        minSdk = 26
        targetSdk = 36
        versionCode = 2
        versionName = "1.2.0"
        manifestPlaceholders["admobAppId"] = appId
        buildConfigField("String", "BANNER_AD_UNIT_ID", "\"" + bannerId + "\"")
        buildConfigField("boolean", "USES_LIVE_ADS", liveAds.toString())
    }
    buildFeatures { buildConfig = true }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}

dependencies {
    implementation("com.google.android.gms:play-services-ads:25.5.0")
    implementation("com.google.android.ump:user-messaging-platform:4.0.0")
}
