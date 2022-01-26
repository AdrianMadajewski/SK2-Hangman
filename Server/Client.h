#ifndef CLIENT_H
#define CLIENT_H

#include "Handler.h"
#include "Utility.h"
#include "MessageBuilder.h"

#include <unordered_set>
#include <string>
#include <iostream>
#include <string>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/epoll.h>

class Client : public Handler
{
public:
    Client(int socket, sockaddr_in adress);
    void setNickname(const std::string &nickname);
    virtual ~Client();
    void sendToOne(Client *client, const MessageBuilder &message);
    void sendToAll(const MessageBuilder &message);
    void hostReady();
    void reset();
    void setNewWord();
    void sendWinner();
    static std::unordered_set<Client*> getClients();
    void handleReceivedMessage(const MessageBuilder &info);
    void guessed_letter(const std::string &message);
    void newPlayer(const std::string &nickname);
    virtual void handleEvent(uint32_t events) override;
    sockaddr_in getAddress() const { return m_address; }
    void serverMessage(const std::string &message) const;
    void sendToAllButOne(Client* client, const MessageBuilder &message);
private:
    sockaddr_in m_address;
    inline static std::unordered_set<Client*> s_clients{};
    inline static std::string s_word{"haslo"};
    inline static int s_id {0};
    int m_id;
    int m_guessed;
    int m_missed;
    bool m_host;
    std::string m_nickname;
    const static int MAX_GUESS = 5;
};

#endif