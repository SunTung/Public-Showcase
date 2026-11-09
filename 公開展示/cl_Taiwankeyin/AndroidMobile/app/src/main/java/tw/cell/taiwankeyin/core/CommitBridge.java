package tw.cell.taiwankeyin.core;

import java.util.List;
import java.util.function.Consumer;
import java.util.function.UnaryOperator;

/** The editing app must accept text before the IME clears its preedit or learns it. */
public final class CommitBridge {
    private CommitBridge() { }
    @FunctionalInterface public interface TextTarget { boolean commit(String text); }

    /** Returns false without modifying composition when the target rejects input.
     * A local learning failure must never retract text successfully sent to the editor. */
    public static boolean commitCandidate(KeyinCore.Session session, KeyinCore.Memory memory,
            int index, TextTarget target, Consumer<RuntimeException> onLearningFailure) {
        return commitCandidate(session,memory,index,target,onLearningFailure,UnaryOperator.identity());
    }

    /** Transform the accepted candidate into its final script BEFORE both commit and learning. */
    public static boolean commitCandidate(KeyinCore.Session session, KeyinCore.Memory memory,
            int index, TextTarget target, Consumer<RuntimeException> onLearningFailure,
            UnaryOperator<String> outputTransform) {
        if (session == null || target == null || memory == null || outputTransform == null) return false;
        List<KeyinCore.Candidate> options = session.candidates();
        if (index < 0 || index >= options.size()) return false;
        // Keep the chosen phonetic reading before Android's input callbacks can change state.
        KeyinCore.Candidate selected = options.get(index);
        String emitted = outputTransform.apply(selected.text);
        if (emitted == null || emitted.isEmpty() || !target.commit(emitted)) return false;
        session.clear();
        try {
            memory.committed(emitted, selected.reading);
        } catch (RuntimeException ex) {
            if (onLearningFailure != null) onLearningFailure.accept(ex);
        }
        return true;
    }
}
