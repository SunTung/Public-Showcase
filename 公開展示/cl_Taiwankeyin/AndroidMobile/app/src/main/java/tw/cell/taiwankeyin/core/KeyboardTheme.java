package tw.cell.taiwankeyin.core;

/** Fixed offline keyboard palettes; each choice persists as a small integer. */
public final class KeyboardTheme {
    private KeyboardTheme() {}
    public static final class Palette {
        public final int index;
        public final String name;
        public final int background, panel, accent, text;
        private Palette(int i, String n, int b, int p, int a, int t) {
            index=i; name=n; background=b; panel=p; accent=a; text=t;
        }
    }
    private static final Palette[] PALETTES = {
        new Palette(0,"深藍",0xFF161E2B,0xFF273346,0xFF3F95E5,0xFFF4F7FC),
        new Palette(1,"深灰",0xFF202124,0xFF383A40,0xFF80868B,0xFFFFFFFF),
        new Palette(2,"紫色",0xFF20172F,0xFF433154,0xFF915BD1,0xFFF9F2FF),
        new Palette(3,"綠色",0xFF132821,0xFF254638,0xFF168B65,0xFFF0FFF7),
        new Palette(4,"暖橙",0xFF30231B,0xFF564033,0xFFE58B42,0xFFFFF5EE),
        new Palette(5,"淺色",0xFFF4F5F8,0xFFD9DDE8,0xFF487CD8,0xFF182235)
    };
    public static final int RANDOM_MODE = 6;
    public static int count() { return PALETTES.length; }
    public static int modeCount() { return count()+1; }
    public static int randomKeyColor(java.util.Random random, int previous) {
        // One of six existing accent colors, avoid leaving an individual key unchanged.
        int first = random.nextInt(count());
        if (PALETTES[first].accent == previous) first = (first+1+random.nextInt(count()-1))%count();
        return PALETTES[first].accent;
    }
    public static int readableText(int background) {
        int r=(background>>16)&255,g=(background>>8)&255,b=background&255;
        int luminance=(299*r+587*g+114*b)/1000;
        return luminance>145 ? 0xFF17212C : 0xFFFFFFFF;
    }
    public static Palette get(int index) { return PALETTES[index >= 0 && index < PALETTES.length ? index : 0]; }
}
