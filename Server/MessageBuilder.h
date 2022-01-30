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
    PASSWORD = 4,
    GUESS = 5, 
    WINNER = 6, 
    RESET = 7, 
    RECONNECT = 8, 
    REMOVE = 9, 
};

std::string MessageCodeToString(MessageCode code);

class MessageBuilder
{
private:
    int m_message_length;
    MessageCode m_code;
    std::string m_contents;
public:  
    MessageBuilder(MessageCode code, const std::string &message, int length) : 
        m_message_length(length), m_code(code), m_contents(message) {}
    MessageBuilder(MessageCode code) : m_message_length(0), m_code(code), m_contents("") {}
    int getMessageLength() const { return m_message_length; } 
    MessageCode getMessageCode() const { return m_code; } 
    std::string getContents() const { return m_contents; } 

    std::string serialize() const;

    friend std::ostream& operator<<(std::ostream& stream, const MessageBuilder& builder);
};

#endif