#include "cellkeyin/store.hpp"
#include <stdexcept>
#include <string>
namespace cellkeyin {
namespace {
struct Statement {
 sqlite3_stmt* stmt=nullptr;
 Statement(sqlite3* db, const char* sql) {
  if(sqlite3_prepare_v2(db,sql,-1,&stmt,nullptr)!=SQLITE_OK) throw std::runtime_error(sqlite3_errmsg(db));
 }
 ~Statement(){ sqlite3_finalize(stmt); }
 void bind(int i,const std::string& s){
  if(sqlite3_bind_text(stmt,i,s.data(),static_cast<int>(s.size()),SQLITE_TRANSIENT)!=SQLITE_OK) throw std::runtime_error("bind failed");
 }
};
}
Store::Store(const std::string& path) {
 if(sqlite3_open_v2(path.c_str(),&db_,SQLITE_OPEN_READWRITE|SQLITE_OPEN_CREATE|SQLITE_OPEN_FULLMUTEX,nullptr)!=SQLITE_OK) {
  const std::string msg = db_ ? sqlite3_errmsg(db_) : "sqlite open failure";
  if(db_) sqlite3_close(db_);
  db_=nullptr;
  throw std::runtime_error(msg);
 }
 try {
  sqlite3_busy_timeout(db_,5000);
  if(path!=":memory:") exec("PRAGMA journal_mode=WAL");
  exec("PRAGMA foreign_keys=ON");
  exec("PRAGMA secure_delete=ON");
  exec("CREATE TABLE IF NOT EXISTS schema_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL)");
  exec("INSERT OR IGNORE INTO schema_meta VALUES('version','1')");
  exec("CREATE TABLE IF NOT EXISTS phrase_stats(text TEXT PRIMARY KEY,n INTEGER NOT NULL CHECK(n BETWEEN 1 AND 10),seen INTEGER NOT NULL DEFAULT 0,last_seen INTEGER NOT NULL DEFAULT 0)");
  exec("CREATE TABLE IF NOT EXISTS context_edges(context_key TEXT NOT NULL,text TEXT NOT NULL,seen INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(context_key,text))");
  exec("CREATE TABLE IF NOT EXISTS choice_stats(reading TEXT NOT NULL,text TEXT NOT NULL,seen INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(reading,text))");
  exec("CREATE TABLE IF NOT EXISTS rejections(context_key TEXT NOT NULL,text TEXT NOT NULL,seen INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(context_key,text))");
 } catch(...) { sqlite3_close(db_);db_=nullptr;throw; }
}
Store::~Store(){ if(db_) sqlite3_close(db_); }
void Store::exec(const char* sql) const {
 char* err=nullptr;
 if(sqlite3_exec(db_,sql,nullptr,nullptr,&err)!=SQLITE_OK){std::string msg=err?err:"sql failed";sqlite3_free(err);throw std::runtime_error(msg);}
}
void Store::upsert(const char* sql,const std::string& a,const std::string& b) const {
 Statement st(db_,sql);st.bind(1,a);if(sqlite3_bind_parameter_count(st.stmt)>=2)st.bind(2,b);
 if(sqlite3_step(st.stmt)!=SQLITE_DONE)throw std::runtime_error(sqlite3_errmsg(db_));
}
int64_t Store::count(const char* sql,const std::string& a,const std::string& b) const {
 Statement st(db_,sql);st.bind(1,a);if(sqlite3_bind_parameter_count(st.stmt)>=2)st.bind(2,b);
 if(sqlite3_step(st.stmt)!=SQLITE_ROW) throw std::runtime_error(sqlite3_errmsg(db_));
 return sqlite3_column_int64(st.stmt,0);
}
void Store::record_phrase(const std::string& p,size_t n) {
 if(n<1||n>10)throw std::invalid_argument("phrase length outside [1,10]");
 Statement st(db_,"INSERT INTO phrase_stats(text,n,seen,last_seen) VALUES(?1,?2,1,strftime('%s','now')) ON CONFLICT(text) DO UPDATE SET seen=seen+1,last_seen=excluded.last_seen");
 st.bind(1,p);
 if(sqlite3_bind_int64(st.stmt,2,static_cast<sqlite3_int64>(n))!=SQLITE_OK||sqlite3_step(st.stmt)!=SQLITE_DONE)throw std::runtime_error(sqlite3_errmsg(db_));
}
void Store::record_choice(const std::string& reading,const std::string& selected,const std::string& key) {
 if(!key.empty()) upsert("INSERT INTO context_edges(context_key,text,seen) VALUES(?1,?2,1) ON CONFLICT(context_key,text) DO UPDATE SET seen=seen+1",key,selected);
 if(!reading.empty()) upsert("INSERT INTO choice_stats(reading,text,seen) VALUES(?1,?2,1) ON CONFLICT(reading,text) DO UPDATE SET seen=seen+1",reading,selected);
}
void Store::record_rejection(const std::string& key,const std::string& candidate) {
 upsert("INSERT INTO rejections(context_key,text,seen) VALUES(?1,?2,1) ON CONFLICT(context_key,text) DO UPDATE SET seen=seen+1",key,candidate);
}
int64_t Store::phrase_count(const std::string& p) const {return count("SELECT COALESCE((SELECT seen FROM phrase_stats WHERE text=?1),0)",p);}
int64_t Store::choice_count(const std::string& r,const std::string& p) const {return count("SELECT COALESCE((SELECT seen FROM choice_stats WHERE reading=?1 AND text=?2),0)",r,p);}
int64_t Store::edge_count(const std::string& key,const std::string& p) const {return count("SELECT COALESCE((SELECT seen FROM context_edges WHERE context_key=?1 AND text=?2),0)",key,p);}
int64_t Store::rejection_count(const std::string& key,const std::string& p) const {return count("SELECT COALESCE((SELECT seen FROM rejections WHERE context_key=?1 AND text=?2),0)",key,p);}
int64_t Store::last_seen(const std::string& p) const {return count("SELECT COALESCE((SELECT last_seen FROM phrase_stats WHERE text=?1),0)",p);}
void Store::begin_transaction() {exec("BEGIN IMMEDIATE TRANSACTION");}
void Store::commit_transaction() {exec("COMMIT");}
void Store::rollback_transaction() {exec("ROLLBACK");}
void Store::clear() {
 begin_transaction();
 try { exec("DELETE FROM phrase_stats");exec("DELETE FROM context_edges");exec("DELETE FROM choice_stats");exec("DELETE FROM rejections");commit_transaction(); }
 catch(...) { try { rollback_transaction();}catch(...){} throw; }
 // Compact pages and truncate the WAL after user requests a reset. This is not a disk-forensic erasure guarantee.
 exec("VACUUM");
 exec("PRAGMA wal_checkpoint(TRUNCATE)");
}
}
