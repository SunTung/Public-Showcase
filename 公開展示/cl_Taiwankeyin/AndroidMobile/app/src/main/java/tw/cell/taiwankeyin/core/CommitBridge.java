package tw.cell.taiwankeyin.core;

import java.util.List;
import java.util.function.Consumer;

/** The editing app must accept text before the IME clears its preedit or learns it. */
public final class CommitBridge {
    private CommitBridge() { }
    @FunctionalInterface public interface TextTarget { boolean commit(String text); }

    /** Returns false without modifying composition when the target rejects input.
     * A local learning failure must never retract text successfully sent to the editor. */
    public static boolean commitCandidate(KeyinCore.Session session, KeyinCore.Memory memory,
            int index, TextTarget target, Consumer<RuntimeException> onLearningFailure) {
        if (session == null || target == null || memory == null) return false;
        List<KeyinCore.Candidate> options = session.candidates();
        if (index < 0 || index >= options.size()) return false;
        // Keep the chosen phonetic reading before Android's input callbacks can change state.
        KeyinCore.Candidate selected = options.get(index);
        if (!target.commit(selected.text)) return false;
        session.clear();
        try {
            memory.committed(selected.text, selected.reading);
        } catch (RuntimeException ex) {
            if (onLearningFailure != null) onLearningFailure.accept(ex);
        }
        return true;
    }
}
