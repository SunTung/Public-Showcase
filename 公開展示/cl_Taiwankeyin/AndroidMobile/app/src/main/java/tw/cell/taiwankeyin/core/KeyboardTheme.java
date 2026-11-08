package tw.cell.taiwankeyin.core;

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
    public static int count() { return PALETTES.length; }
    public static Palette get(int index) { return PALETTES[index >= 0 && index < PALETTES.length ? index : 0]; }
}
