#include "MessageBuilder.h"

std::string MessageCodeToString(MessageCode code) 
{
    switch(code)
    {
        case HOST_INIT:     return "HOST_INIT";
        case NEW_PLAYER:    return "NEW_PLAYER";
        case NICK_TAKEN:    return "NICK_TAKEN";
        case HOST_READY:    return "HOST_READY";
        case GUESS:         return "GUESS";
        case PASSWORD:      return "PASSWORD";
        case WINNER:        return "WINNER";
        case RESET:         return "RESET";
        case RECONNECT:     return "RECONNECT";
        case REMOVE:        return "REMOVE";
        case ERROR: 
        default:
            return "ERROR";
    }
}

static std::string prependWithSize(std::string &s)
{ 
    return (s.size() >= 10 ? std::to_string(s.size()) : "0" + std::to_string(s.size()));
}

std::string MessageBuilder::serialize() const
{
    std::string build; 
    build += std::to_string(static_cast<int>(m_code));
    build += m_contents;
    build = build.insert(0, prependWithSize(build));
    return build;
}

std::ostream& operator<<(std::ostream& stream, const MessageBuilder& builder)
{
    stream << "Builder[" << std::endl << 
        " length = " << builder.m_message_length << "," << std::endl << 
        " code = " << MessageCodeToString(builder.m_code) << "," << std::endl <<
        " contents = " << (builder.m_contents.length() == 0 ? "NONE" : builder.m_contents) << std::endl <<
    "];" << std::endl;
    return stream;
}