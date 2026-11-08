#include "cellkeyin/unicode.hpp"
#include <unicode/brkiter.h>
#include <unicode/locid.h>
#include <unicode/unistr.h>
#include <unicode/ustring.h>
#include <memory>
#include <stdexcept>
#include <vector>
namespace cellkeyin {
std::vector<std::string> graphemes(const std::string& utf8) {
 UErrorCode status = U_ZERO_ERROR;
 int32_t required=0;
 u_strFromUTF8(nullptr,0,&required,utf8.data(),static_cast<int32_t>(utf8.size()),&status);
 if (status != U_BUFFER_OVERFLOW_ERROR && U_FAILURE(status)) throw std::invalid_argument("invalid UTF-8");
 status = U_ZERO_ERROR;
 std::vector<UChar> chars(static_cast<size_t>(required)+1);
 u_strFromUTF8(chars.data(),static_cast<int32_t>(chars.size()),nullptr,utf8.data(),static_cast<int32_t>(utf8.size()),&status);
 if (U_FAILURE(status)) throw std::invalid_argument("invalid UTF-8");
 icu::UnicodeString u(chars.data(),required);
 std::unique_ptr<icu::BreakIterator> itr(icu::BreakIterator::createCharacterInstance(icu::Locale("zh", "TW"),status));
 if (U_FAILURE(status) || !itr) throw std::runtime_error("ICU break iterator failure");
 itr->setText(u);
 std::vector<std::string> result;
 for (int32_t start=itr->first(), end=itr->next();end!=icu::BreakIterator::DONE;start=end,end=itr->next()) {
  std::string cluster;
  u.tempSubStringBetween(start,end).toUTF8String(cluster);
  result.push_back(std::move(cluster));
 }
 return result;
}
bool hard_break(const std::string& c) {
 return c=="，"||c=="。"||c=="！"||c=="？"||c=="、"||c=="；"||c==","||c=="."||c=="!"||c=="?"||c==";"||c=="\n"||c=="\r"||c=="\r\n";
}
bool soft_connector(const std::string& c) {
 return c=="（"||c=="）"||c=="〔"||c=="〕"||c=="〈"||c=="〉"||c=="｛"||c=="｝"||c=="：";
}
size_t effective_length(const std::string& text) {
 size_t n=0;
 for(const auto& c:graphemes(text)) if(!soft_connector(c)&&!hard_break(c)) ++n;
 return n;
}
}
