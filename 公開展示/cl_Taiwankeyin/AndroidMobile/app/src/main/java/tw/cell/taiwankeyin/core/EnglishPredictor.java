package tw.cell.taiwankeyin.core;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

/** Strict prefix-only English candidates. No Chinese learning database or random history. */
public final class EnglishPredictor {
    private static final String[] WORDS = (
        "hello help helmet helpful helping helped world thanks thank thankyou please sorry yes no okay ok good morning evening afternoon goodbye welcome the to and of a in is it you that he was for on are with as I his they be at one have this from or had by hot word but what some we can out other were all there when up use your how said an each she which do their time if will way about many then them would write like so these her long make thing see him two has look more day could go come did number sound no most people my over know water than call first who may down side been now find any new work part take get place made live where after back little only round man year came show every good me give our under name very through just form sentence great think say help low line differ turn cause much mean before move right boy old too same tell does set three want air well also play small end put home read hand port large spell add even land here must big high such follow act why ask men change went light kind off need house picture try us again animal point mother world near build self earth father head stand own page should country found answer school grow study still learn plant cover food sun four thought let keep eye never last door between city tree cross since hard start might story saw far sea draw left late run don't while press close night real life few north open seem together next white children begin got walk example ease paper group always music those both mark often letter until mile river car feet care second book carry took science eat room friend began idea fish mountain stop once base hear horse cut sure watch color face wood main enough plain girl usual young ready above ever red list though feel talk bird soon body dog family direct pose leave song measure state product black short numeral class wind question happen complete ship area half rock order fire south problem piece told knew pass farm top whole king size heard best hour better true during hundred five remember step early hold west ground interest reach fast verb sing listen six table travel less morning ten simple several vowel toward war lay against pattern slow center love person money serve appear road map rain rule govern pull cold notice voice unit power town fine certain fly fall lead cry dark machine note wait plan figure star box noun field rest correct able pound done beauty drive stood contain front teach week final gave green oh quick develop ocean warm free minute strong special mind behind clear tail produce fact street inch lot nothing course stay wheel full force blue object decide surface deep moon island foot system busy test record boat common gold possible plane age dry wonder laugh thousand ago ran check game shape yes miss brought heat snow bed bring sit perhaps fill east weight language among").split(" ");
    private static final List<String> DICTIONARY;
    static {
        ArrayList<String> words = new ArrayList<>(Arrays.asList(WORDS));
        // Input order is an approximate frequency prior, not alphabetical order.
        DICTIONARY = Collections.unmodifiableList(words);
    }
    private EnglishPredictor() {}

    public static String prefixFromText(String preceding) {
        if (preceding == null || preceding.isEmpty()) return "";
        int i = preceding.length();
        while (i > 0 && isLetter(preceding.charAt(i-1))) i--;
        String suffix = preceding.substring(i);
        return suffix.length() <= 32 ? suffix : "";
    }
    private static boolean isLetter(char c) {
        return c >= 'a' && c <= 'z' || c >= 'A' && c <= 'Z';
    }
    public static List<String> predict(String typed, int limit) {
        if (typed == null || typed.isEmpty() || limit <= 0) return Collections.emptyList();
        String prefix = typed.toLowerCase(Locale.ROOT);
        if (prefix.length() > 32 || !prefix.matches("[a-z]+")) return Collections.emptyList();
        ArrayList<String> result = new ArrayList<>();
        for (String word : DICTIONARY) {
            if (word.length() > prefix.length() && word.startsWith(prefix)) {
                result.add(Character.isUpperCase(typed.charAt(0))
                    ? Character.toUpperCase(word.charAt(0)) + word.substring(1) : word);
                if (result.size() == limit) break;
            }
        }
        return result;
    }
    public static boolean validChoice(String typed, String selected) {
        return typed != null && selected != null && selected.length() > typed.length()
            && selected.toLowerCase(Locale.ROOT).startsWith(typed.toLowerCase(Locale.ROOT))
            && selected.matches("[A-Za-z]+");
    }
}
