#ifndef MESSAGE_H
#define MESSAGE_H

#include <string>
#include <vector>
#include <iostream>

enum MessageCode
{
    ERROR = -1,
    HOST_INIT = 0,
    NEW_PLAYER = 1,
    NICK_TAKEN = 2,
    HOST_READY = 3, 
    GUESS = 4,
    WINNER = 5, // TODO:
    RESET = 6,
    RECONNECT = 7, // TODO:
};

std::string MessageCodeToString(MessageCode code);

// TODO: id klientow moze wiec wieksze > 9

class MessageBuilder
{
private:
    int m_message_length;
    MessageCode m_code;
    std::string m_contents;
public:
    MessageBuilder(MessageCode code, const std::string &message, int length) : 
        m_message_length(length + 1), m_code(code), m_contents(message) {}
    int getMessageLength() const { return m_message_length; } 
    MessageCode getMessageCode() const { return m_code; } 
    std::string getContents() const { return m_contents; } 

    std::string serialize();

    friend std::ostream& operator<<(std::ostream& stream, const MessageBuilder& builder);
};

#endif