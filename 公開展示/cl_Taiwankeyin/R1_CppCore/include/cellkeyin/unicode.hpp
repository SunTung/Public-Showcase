#pragma once
#include <string>
#include <vector>
namespace cellkeyin {
std::vector<std::string> graphemes(const std::string& utf8);
bool hard_break(const std::string& cluster);
bool soft_connector(const std::string& cluster);
size_t effective_length(const std::string& utf8);
}
