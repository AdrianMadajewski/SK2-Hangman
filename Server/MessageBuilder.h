#ifndef MESSAGE_H
#define MESSAGE_H

#include <string>
#include <vector>
#include <iostream>

class MessageBuilder
{
public:
    enum Code
    {
        ERROR = -1,
        HOST_INITIAL = 0,
        NEW_PLAYER = 1,
        NICK_TAKEN = 2,
        HOST_READY = 3,
        NEW_LETTER = 4, 
        RESET = 5,
        RECONNECT = 6,
    };

    struct Info
    {
        int length;
        Code code;
        std::string content;

        Info(int _length, Code _code, std::string _content) :
            length(_length), code(_code), content(_content) {}
        Info() = default;
        Info(Code _code, std::string _content) : 
            code(_code), content(_content)
        {
            length = content.size() + 1;
        }

        std::string serialize()
        {
            return MessageBuilder::serialize(*this);
        }

        friend std::ostream& operator<< (std::ostream& stream, const Info& m)
        {
            stream << m.length << std::endl;
            stream << m.code << std::endl;
            stream << m.content << std::endl;
            return stream;
        } 
    };

    static std::string serialize(const MessageBuilder::Info &info);
    static MessageBuilder::Info deserialize(std::string &message);
};

#endif