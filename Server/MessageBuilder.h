#ifndef MESSAGE_H
#define MESSAGE_H

#include <string>
#include <vector>
#include <iostream>

enum MessageCode
{
    ERROR = -1, //unhandled
    HOST_INIT = 0, // ok
    NEW_PLAYER = 1, // ok
    NICK_TAKEN = 2, // ok
    HOST_READY = 3, // ok
    PASSWORD = 4, // ok
    GUESS = 5, // ok
    WINNER = 6, // ok
    RESET = 7, // ok - tego nie handluje gdybys ty od siebie chcial zresetowac
    RECONNECT = 8, // TODO:
    REMOVE = 9, // ok
};

std::string MessageCodeToString(MessageCode code);

// TODO: id klientow moze wiec wieksze > 9 ale id jest w sumie totalnie nie wazne to jebac

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