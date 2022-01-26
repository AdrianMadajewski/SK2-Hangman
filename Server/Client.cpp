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
    MessageBuilder info(
        MessageCode::REMOVE,
        this->m_nickname,
        this->m_nickname.size()
    );

    sendToAllButOne(this, info);
    serverMessage("Removing connection from: ");
    s_clients.erase(this);
    epoll_ctl(epoll_fd, EPOLL_CTL_DEL, m_socket, nullptr);
    shutdown(m_socket, SHUT_RDWR);
    close(m_socket);
}

void Client::serverMessage(const std::string &message) const
{
    std::cout << message <<  inet_ntoa(m_address.sin_addr) << ":" << ntohs(m_address.sin_port) <<
            " (fd: " << m_socket << ")" << std::endl;
}

void Client::handleEvent(uint32_t events) 
{   
    // MAKE THIS ASSYNCHRONOUS
    if(events & EPOLLIN) {
        int in_message_size;
        char buffer[2]{};
        int count = recv(m_socket, &buffer, 2, MSG_WAITALL);

        in_message_size = atoi(buffer);

        if(count > 0)
        {
            // Received data (in_message_size) - how many bytes was sent
            std::string data(in_message_size, 0);
            count = recv(m_socket, (void*)data.data(), in_message_size, MSG_WAITALL);

            // Received more data - full serialized message
            if(count > 0)
            {
                // Size already gotten
                MessageCode code = static_cast<MessageCode>(data[0] - '0'); 
                // substr - code already gotten
                // size - 1 because builder adds + 1 for message code
                MessageBuilder info(code, data.substr(1, data.size()), in_message_size - 1);
                
                serverMessage("Message received from: ");
                std::cout << info << std::endl;

                handleReceivedMessage(info);

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

void Client::sendWinner()
{
    MessageBuilder info(MessageCode::WINNER, this->m_nickname, this->m_nickname.size());
    sendToAll(info);
}

void Client::handleReceivedMessage(const MessageBuilder &info)
{
    switch(info.getMessageCode())
    {
        case NEW_PLAYER:
            newPlayer(info.getContents()); // ok
            break;
        case HOST_READY:
            hostReady(); // ok
            break;
        case GUESS:
            guessed_letter(info.getContents()); // ok
            break;
        case RESET:    
            reset(); // ok
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
    
void Client::sendToOne(Client *client, const MessageBuilder &message)
{
    serverMessage("Message send to: ");
    std::cout << message << std::endl;
    if(send(client->m_socket, message.serialize().data(), message.serialize().size(), 0) > 0) {
        return;
    }
    error("Send failed to client: " + client->m_nickname);
}

void Client::sendToAllButOne(Client* theClient, const MessageBuilder &message)
{
    for(const auto &client: s_clients) {
        if(client == theClient) {
            continue;
        }
        sendToOne(client, message);
    }
}

void Client::sendToAll(const MessageBuilder &message)
{
    // Send to all players
    for(const auto &client : s_clients) 
    {
       sendToOne(client, message);
    }
}

void Client::hostReady()
{
    if(this->m_host)
    {
        MessageBuilder ready(MessageCode::PASSWORD,
            s_word,
            s_word.size()
        );

        sendToAll(ready);
    }
}

void Client::guessed_letter(const std::string &message)
{
    // Check for winner
    if(this->m_guessed == this->s_word.size() && this->m_missed != MAX_GUESS)
    {
        MessageBuilder winner(
            MessageCode::WINNER,
            this->m_nickname,
            this->m_nickname.size()
        );
        sendToAll(winner);
        return;
    }

    // Check for looser
    if(this->m_missed == MAX_GUESS)
    {
        // Michalek mowi zeby go nie usuwac z lobby bo on sobie bedzie liczyl a ja uwazam inaczej :((
        return;
    }

    // Normal gameplay
    if(message[0] == '0') 
    {
         m_missed++;
    }
    else if(message[0] == '1')
    {
        m_guessed++;
    }  
    
    // Update all clients with ranking
    // nick{trafione}:{nietrafione}

    std::string response = this->m_nickname + std::to_string(this->m_guessed) + ":" + std::to_string(this->m_missed);
    MessageBuilder info(
        MessageCode::GUESS,
        response,
        response.size()  
    );

    sendToAll(info);
    
}

void Client::reset()
{
    // Zero stats
    for(auto &clients : s_clients) 
    {
        clients->m_guessed = 0;
        clients->m_missed = 0;
    }

    setNewWord();

    // Build response
    MessageBuilder info(MessageCode::RESET);

    // Send to all reset code
    sendToAll(info);
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
            MessageCode::HOST_INIT
        );
        this->setNickname(nickname);
        sendToOne(this, info);
    }
    else
    {
        for(auto &client : s_clients) {
            if(client->m_nickname == nickname) {
                std::cout << "Invalid nickname - duplicate: " << nickname << std::endl;
                // MessageBuilder::Info info(MessageBuilder::NICK_TAKEN, "taken");
                MessageBuilder info(
                    MessageCode::NICK_TAKEN
                );

                sendToOne(client, info);
                // to cie wykurwia z bazy calkowicie i wysyla wiadomosc o remove do reszty
                delete client;
                // ale jakbys mial to wyjebac to tu musisz odeslac wiadomosc do tego gracza ze ma NICK_TAKEN
                // MessageBuilder info(MessageCode::NICK_TAKEN);
                // sendToOne(this, info);
                return;
            }
        }

        // New valid player
        
        this->setNickname(nickname);
        
        MessageBuilder info(
            MessageCode::NEW_PLAYER,
            this->m_nickname,
            this->m_nickname.size()
        );

        // 1 2 3
        sendToAll(info); // nick3 -> 1 2 3

        for (const auto &client :s_clients)
        {
            if(client == this) {
                continue;
            }
            MessageBuilder info(
                MessageCode::NEW_PLAYER,
                client->m_nickname,
                client->m_nickname.size()
            );
            sendToOne(this, info); // nik1 nick2 ->nick3
        }
    }
}