#ifndef APP_H
#define APP_H

#include <vector>
#include <string>

class Application
{
private:
    inline static std::vector<std::string> s_words{};
    inline static int s_index{0};
    int epoll_fd;
public:
    void run(long port, const std::string &dictionary);
};

#endif