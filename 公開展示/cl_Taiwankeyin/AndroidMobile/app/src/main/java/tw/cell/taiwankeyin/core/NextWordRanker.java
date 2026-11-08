package tw.cell.taiwankeyin.core;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Merge user-learned next phrases with frequency-backed dictionary completions.
 * No input data leaves the device; only confirmed text contributes to context.
 */
public final class NextWordRanker {
    private NextWordRanker() {}
    public static final class Hit {
        public final String suffix;
        public final int frequency;
        public final int prefixUnits;
        public Hit(String suffix,int frequency,int prefixUnits) {
            this.suffix=suffix;this.frequency=frequency;this.prefixUnits=prefixUnits;
        }
    }
    public static List<String> merge(List<String> learned, List<Hit> dictionary, int limit) {
        if (limit <= 0) return Collections.emptyList();
        Map<String,Double> rank=new HashMap<>();
        if (dictionary != null) for (Hit hit : dictionary) {
            if (!usable(hit.suffix)) continue;
            double score=Math.log1p(Math.max(0,hit.frequency))*12.0
                    +Math.max(0,hit.prefixUnits)*3.5;
            rank.merge(hit.suffix, score, Math::max);
        }
        if (learned != null) for (int i=0;i<learned.size();i++) {
            String next=learned.get(i);
            if (usable(next)) rank.merge(next, 200.0-i, Math::max);
        }
        List<Map.Entry<String,Double>> entries=new ArrayList<>(rank.entrySet());
        entries.sort(Comparator.<Map.Entry<String,Double>>comparingDouble(Map.Entry::getValue)
                .reversed().thenComparing(Map.Entry::getKey));
        List<String> results=new ArrayList<>();
        for (Map.Entry<String,Double> e:entries) {
            results.add(e.getKey());
            if (results.size()>=limit) break;
        }
        return results;
    }
    public static boolean usable(String suffix) {
        if (suffix == null || suffix.isEmpty()) return false;
        int units=KeyinCore.units(suffix).size();
        if (units > 3) return false;
        for (int i=0;i<suffix.length();) {
            int cp=suffix.codePointAt(i);i+=Character.charCount(cp);
            if (!Character.isLetter(cp) && !Character.isDigit(cp)) return false;
        }
        return true;
    }
}
