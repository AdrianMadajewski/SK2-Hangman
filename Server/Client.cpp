#include "Client.h"
#include "MessageBuilder.h"

Client::Client(int socket, const std::string nickname) : m_socket(socket), m_nickname(nickname)
{
    m_host = (s_id == 0 ? true : false);
    m_id = s_id++;
    m_guessed = 0;
    m_missed = 0;
    s_clients.insert(this);
}
Client::~Client()
{
    s_clients.erase(this);
    delete this;
    shutdown(m_socket, SHUT_RDWR);
    close(m_socket);
}
    
void Client::sendToOne(Client *client, const std::string &message)
{
    if(send(client->m_socket, message.data(), message.size(), 0) > 0) {
        return;
    }
    error("Send failed to client: " + client->m_nickname);
}

void Client::sendToAll(const std::string &message)
{
    // Send to all players
    for(const auto &client : s_clients) 
    {
       sendToOne(client, message.data());
    }
}

void Client::sendToOne(Client *client, const std::string &message)
{
    if(send(client->m_socket, message.data(), message.size(), 0) > 0) {
        return;
    }
    error("Send failed to client: " + client->m_nickname);
}

bool Client::hostReady()
{
    MessageBuilder::Info info;
    info.code = MessageBuilder::HOST_READY;
    info.length = 1;

    if(m_host == true)
    {
        sendToAll(MessageBuilder::serialize(info));
        return true;
    }
    else
    {
        return false;
    }
}
bool Client::reset()
{
    // Zero stats
    for(auto &clients : s_clients) 
    {
        clients->m_guessed = 0;
        clients->m_missed = 0;
    }

    setNewWord();

    // Build response
    MessageBuilder::Info info(MessageBuilder::RESET, s_word);

    // Send to all new password
    sendToAll(MessageBuilder::serialize(info));
}
void Client::setNewWord()
{
    int dice = random::generateNumber(0, words.size() - 1);
    s_word = words[dice];
}
std::unordered_set<Client*> Client::getClients()
{
    return s_clients;
}
void Client::newPlayer(int socket, const std::string &nickname)
{
    if(s_id == 0) 
    {
        Client *client = new Client(socket, nickname);
        // First player is considered as host
        MessageBuilder::Info info(
            MessageBuilder::HOST_INITIAL, 
            nickname + std::to_string(client->m_id)
        );

        sendToAll(info.serialize());
    }
    else
    {
        for(const auto &client : s_clients) {
            if(client->m_nickname == nickname) {
                std::cout << "Invalid nickname - duplicate" << nickname << std::endl;
                MessageBuilder::Info info(MessageBuilder::NICK_TAKEN, "taken");
                sendToOne(client, info.serialize());
                return;
            }
        }

        // No player found with the same nickname
        Client *client = new Client(socket, nickname);
        MessageBuilder::Info info(
            MessageBuilder::NEW_PLAYER, 
            nickname + std::to_string(client->m_id)
        );
        sendToAll(info.serialize());
    }
}