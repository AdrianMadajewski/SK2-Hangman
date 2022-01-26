#include "Client.h"
#include "MessageBuilder.h"

int epoll_fd;

Client::Client(int socket, sockaddr_in client_address) : Handler(socket)
{
    epoll_event ee {EPOLLIN|EPOLLRDHUP, {.ptr=this}};
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, this->m_socket, &ee);
    m_address = client_address;
    m_host = (s_id == 0 ? true : false);
    m_id = s_id++;
    m_guessed = 0;
    m_missed = 0;
    s_clients.insert(this);
}
Client::~Client()
{
    std::cout << "Removing connection from: " << 
            inet_ntoa(m_address.sin_addr) << ":" << ntohs(m_address.sin_port) <<
            " (fd: " << m_socket << ")" << std::endl;

    s_clients.erase(this);
    epoll_ctl(epoll_fd, EPOLL_CTL_DEL, m_socket, nullptr);
    shutdown(m_socket, SHUT_RDWR);
    close(m_socket);
}

void Client::handleEvent(uint32_t events) 
{
    if(events & EPOLLIN) {
        int in_message_size;
        int count = recv(m_socket, (void*)&in_message_size, 2, MSG_WAITALL);

        if(count > 0)
        {
            // Received data (in_message_size) - how many bytes was sent
            std::string data(in_message_size, 0);
            count = recv(m_socket, (void*)data.data(), in_message_size, MSG_WAITALL);

            // Received more data - full serialized message
            if(count > 0)
            {
                handleReceivedMessage(in_message_size, data);
            }
            else // Set error flag
                events |= EPOLLERR;

        }
        else // Set error flag
            events |= EPOLLERR;
        
    }
   
    
    // Fatal error occured on client socket
    if(events & ~EPOLLIN) {
        delete this;
    }
}

void Client::handleReceivedMessage(int size, std::string &data)
{
    // Size already gotten
    MessageCode code = static_cast<MessageCode>(data[0] - '0'); 
    // substr - code already gotten
    // size - 1 because builder adds + 1 for message code
    MessageBuilder info(code, data.substr(0, data.size()), size - 1);

    switch(info.getMessageCode())
    {
        case HOST_INIT:     
        case NEW_PLAYER:
            newPlayer(info.getContents());
            break;
        case HOST_READY:
            // TODO:
            break;
        case GUESS:
            guessed_letter();
            break;
        case WINNER:        
            // TODO:
            break;
        case RESET:    
            reset();
            break;     
        case RECONNECT:    
            // TODO:
            break; 
        case ERROR:
        default:
            // Handle this error 
            break;
    }
}

void Client::setNickname(const std::string &nickname)
{
    m_nickname = nickname;
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

bool Client::hostReady()
{
    return false;
}

void Client::guessed_letter()
{
    std::string response = this->m_nickname + ":" + 
        std::to_string(this->m_guessed) + ":" + std::to_string(this->m_missed);

    MessageBuilder info(
        MessageCode::GUESS,
        response,
        response.size()
    );

    sendToAll(info.serialize());
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
    MessageBuilder info(MessageCode::RESET, s_word, s_word.size());

    // Send to all new password
    sendToAll(info.serialize());
    return true;
}

void Client::setNewWord()
{
    // int dice = MyRandom::generateNumber(0, words.size() - 1);
    // s_word = words[dice];
}

std::unordered_set<Client*> Client::getClients()
{
    return s_clients;
}

void Client::newPlayer(const std::string &nickname)
{
    if(m_host == true) 
    {
        MessageBuilder info(
            MessageCode::HOST_INIT,
            s_word,
            s_word.size()
        );

        sendToAll(info.serialize());
    }
    else
    {
        for(const auto &client : s_clients) {
            if(client->m_nickname == nickname) {
                std::cout << "Invalid nickname - duplicate" << nickname << std::endl;
                // MessageBuilder::Info info(MessageBuilder::NICK_TAKEN, "taken");
                MessageBuilder info(
                    MessageCode::NICK_TAKEN,
                    "taken",
                    5
                );

                sendToOne(client, info.serialize());
                return;
            }
        }

         MessageBuilder info(
            MessageCode::NEW_PLAYER,
            s_word,
            s_word.size()
        );

        sendToAll(info.serialize());
    }
}