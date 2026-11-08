#pragma once
#include <deque>
#include <string>
#include <vector>
namespace cellkeyin {
class Context10 {
public:
 static constexpr size_t kMaxChars=10;
 void feed(const std::string& cluster);
 void clear();
 std::string text() const;
 size_t effective_size() const { return effective_; }
 std::vector<std::string> suffixes() const;
private:
 struct Token { std::string text; bool effective; };
 std::deque<Token> tokens_;
 size_t effective_=0;
 void trim();
};
}
