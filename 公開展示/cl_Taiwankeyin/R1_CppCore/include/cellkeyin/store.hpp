#pragma once
#include <sqlite3.h>
#include <cstdint>
#include <string>
namespace cellkeyin {
class Store {
public:
 explicit Store(const std::string& path);
 ~Store();
 Store(const Store&) = delete;
 Store& operator=(const Store&) = delete;
 void record_phrase(const std::string& phrase, size_t effective_count);
 void record_choice(const std::string& reading, const std::string& selected, const std::string& context_key);
 void record_rejection(const std::string& context_key, const std::string& candidate);
 int64_t phrase_count(const std::string& phrase) const;
 int64_t choice_count(const std::string& reading, const std::string& phrase) const;
 int64_t edge_count(const std::string& context_key, const std::string& phrase) const;
 int64_t rejection_count(const std::string& context_key, const std::string& phrase) const;
 int64_t last_seen(const std::string& phrase) const;
 void clear();
 void begin_transaction();
 void commit_transaction();
 void rollback_transaction();
private:
 sqlite3* db_ = nullptr;
 void exec(const char* sql) const;
 void upsert(const char* sql, const std::string& a, const std::string& b = {}) const;
 int64_t count(const char* sql, const std::string& a, const std::string& b = {}) const;
};
}
