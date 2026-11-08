#pragma once
#include "cellkeyin/engine.hpp"
#include <cstddef>
#include <map>
#include <optional>
#include <string>
#include <vector>

namespace cellkeyin {

// Standard Dachen keyboard, following Microsoft/Rime standard Taiwan arrangement.
// The first tone is stored explicitly as the combining-independent mark 'ˉ'.
class DachenMap {
public:
 static std::string symbol(char key);
 static bool is_phonetic(char key);
 static bool is_tone(char key);
 static size_t phonetic_key_count();
 static std::string decode(const std::string& keys);
};

class Lexicon {
public:
 void add(const std::string& reading, const std::string& text, double baseline);
 void load_tsv(const std::string& path);
 std::vector<Candidate> lookup(const std::string& reading, size_t limit = 50) const;
 size_t entry_count() const { return size_; }
private:
 std::map<std::string,std::vector<Candidate>> entries_;
 size_t size_ = 0;
};

// A composition session does not learn until select() confirms a candidate.
// The caller is responsible for delivering the confirmed string to its edit surface.
class ZhuyinSession {
public:
 ZhuyinSession(Engine& engine, const Lexicon& lexicon);
 bool key(char key);             // Dachen phonetic keys and tone keys (' ' 6 3 4 7)
 bool backspace();
 void escape();
 bool move_selection(int delta);
 std::optional<std::string> select(size_t index); // explicit confirmed selection
 bool punctuation(const std::string& text);      // only while idle, hard/soft punctuation
 std::string preedit() const;
 std::string reading() const;
 const std::vector<Candidate>& candidates() const { return menu_; }
 size_t selection() const { return selected_; }
 bool active() const { return !raw_.empty() || !completed_.empty(); }
 bool ready() const { return raw_.empty() && !completed_.empty() && !menu_.empty(); }
private:
 struct Syllable {std::string raw; std::string reading;};
 Engine& engine_;
 const Lexicon& lexicon_;
 std::string raw_;
 std::vector<Syllable> completed_;
 std::vector<Candidate> menu_;
 size_t selected_ = 0;
 void refresh_candidates();
 static bool valid_prefix(const std::string& raw);
 static bool valid_syllable(const std::string& raw);
};
}
