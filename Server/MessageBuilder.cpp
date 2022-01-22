#include "MessageBuilder.h"

#include <iostream>

static std::string prependWithSize(std::string &s)
{ 
    return (s.size() >= 10 ? std::to_string(s.size()) : "0" + std::to_string(s.size()));
}

std::string MessageBuilder::serialize(const Info &info)
{
    std::string message = std::to_string(static_cast<int>(info.code));
    message += info.content;
    message = prependWithSize(message) + message;
    return message;
}

static int getLengthFromMessage(std::string &s)
{
    int ret = std::stoi(s.substr(0, 2));
    s.erase(0, 2);
    return ret;
}

static MessageBuilder::Code getMessageCode(std::string &s)
{
    MessageBuilder::Code ret = static_cast<MessageBuilder::Code> ( std::stoi(s.substr(0, 1)) );
    s.erase(0, 1);
    return ret;
}

MessageBuilder::Info MessageBuilder::deserialize(std::string &message)
{
    int length = getLengthFromMessage(message);
    Code code = getMessageCode(message);
    std::string content = message;

    return Info (length, code, content);
}

int main()
{
    MessageBuilder::Info info;
    info.code = MessageBuilder::HOST_READY;
    info.length = 1;
    std::string serialized = info.serialize();
    std::cout << serialized << std::endl;
    std::cout << "------" << std::endl;
    std::cout << MessageBuilder::deserialize(serialized);
    
    return 0;
}