#pragma once
#include "cellkeyin/context.hpp"
#include "cellkeyin/store.hpp"
#include <string>
#include <vector>
namespace cellkeyin {
struct Candidate {
 std::string text;
 double base_score = 0;
 double final_score = 0;
};
std::string context_key(const std::string& context_utf8); // FNV64 index key only: NOT cryptographic secrecy.
class Engine {
public:
 explicit Engine(const std::string& db_path);
 void commit(const std::string& confirmed_utf8, const std::string& reading = {});
 void reject(const std::string& candidate_utf8);
 std::vector<Candidate> rank(const std::string& reading, std::vector<Candidate> candidates) const;
 void set_learning_enabled(bool enabled);
 void set_sensitive(bool sensitive);
 bool learning_enabled() const { return learning_enabled_; }
 bool sensitive() const { return sensitive_; }
 const Context10& context() const { return context_; }
 Store& store() { return store_; }
 const Store& store() const { return store_; }
 void clear_learning();
 void reset_context() { context_.clear(); }
private:
 Store store_;
 Context10 context_;
 bool learning_enabled_ = true;
 bool sensitive_ = false;
};
}
