#include "MessageBuilder.h"

std::string MessageCodeToString(MessageCode code) 
{
    switch(code)
    {
        case HOST_INIT:     return "HOST_INIT";
        case NEW_PLAYER:    return "NEW_PLAYER";
        case NICK_TAKEN:    return "NICK TAKEN";
        case HOST_READY:    return "HOST_READY";
        case GUESS:         return "GUESS";
        case WINNER:        return "WINNER";
        case RESET:         return "RESET";
        case RECONNECT:     return "RECONNECT";
        case ERROR: 
        default:
            return "ERROR";
    }
}

static std::string prependWithSize(std::string &s)
{ 
    return (s.size() >= 10 ? std::to_string(s.size()) : "0" + std::to_string(s.size()));
}

std::string MessageBuilder::serialize()
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
        " contents = " << builder.m_contents << std::endl <<
    "];" << std::endl;
    return stream;
}

int main()
{
    MessageBuilder new_player(NEW_PLAYER, "zeev", 7);
    std::cout << new_player << std::endl;
    std::cout << new_player.serialize() << std::endl;
    std::cout << "--------" << std::endl;

    MessageBuilder nick_taken(NICK_TAKEN, "zeev", 4+1+2);
    std::cout << nick_taken << std::endl;
    std::cout << nick_taken.serialize() << std::endl;
    std::cout << "--------" << std::endl;

    MessageBuilder reset(RESET, "", 1);
    std::cout << reset << std::endl;
    std::cout << reset.serialize() << std::endl;
    std::cout << "--------" << std::endl;

    MessageBuilder win(WINNER, "wygrany", 10);
    std::cout << win << std::endl;
    std::cout << win.serialize() << std::endl;
    std::cout << "--------" << std::endl;

    MessageBuilder guess(GUESS, "", 1+2);
    std::cout << guess << std::endl;
    std::cout << guess.serialize() << std::endl;
    std::cout << "--------" << std::endl;

    MessageBuilder host_ready(HOST_READY, "", 1+2);
    std::cout << host_ready << std::endl;
    std::cout << host_ready.serialize() << std::endl;
    std::cout << "--------" << std::endl;

    return 0;
}