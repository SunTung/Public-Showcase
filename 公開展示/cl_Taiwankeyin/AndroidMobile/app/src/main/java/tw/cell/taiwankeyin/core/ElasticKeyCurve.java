package tw.cell.taiwankeyin.core;

/** Pure Java geometric envelope for the Android elastic visual renderer.
 * It does NOT change any touch target or keyboard layout. */
public final class ElasticKeyCurve {
    private ElasticKeyCurve() {}
    public static final long PRESS_MS = 65L;
    public static final long RECOVER_MS = 240L;
    public static float clamp(float p) { return Math.max(0f,Math.min(1f,p)); }
    public static float scale(float p) { return 1f + 0.125f*clamp(p); }
    public static float cornerDp(float p) { return 7f + 16f*clamp(p); }
    public static float zDp(float p) { return 4f*clamp(p); }
}
