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
    virtual ~Client();

    // Core
    virtual void handleEvent(uint32_t events) override;
    void handleReceivedMessage(const MessageBuilder &info);

    static std::unordered_set<Client*> getClients();

    // Setters
    void setNickname(const std::string &nickname);
    void setNewWord();

    // Static setters
    static void setWords(const std::vector<std::string> &words);
    static void setIndex(const int index);

    // Senders
    void sendToOne(Client *client, const MessageBuilder &message);
    void sendToAll(const MessageBuilder &message);
    void sendToAllButOne(Client* client, const MessageBuilder &message);

    // Messages handlers
    void hostReady();
    void reset();
    void sendWinner();
    void guessed_letter(const std::string &message);
    void newPlayer(const std::string &nickname);

    // Getters
    sockaddr_in getAddress() const { return m_address; }

    // Util
    void displayMessage(const std::string &message) const;

    
private:
    const static int MAX_GUESS = 5;

    inline static std::unordered_set<Client*> s_clients{};
    inline static std::vector<std::string> s_words{};
    inline static int s_id {0};
    inline static int s_index{0};

    int m_id;
    int m_guessed;
    int m_missed;
    bool m_host;

    sockaddr_in m_address;
    std::string m_nickname;
};

#endif