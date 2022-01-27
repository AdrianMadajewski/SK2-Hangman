#include "Client.h"
#include "MessageBuilder.h"

// Gdy klient usuwany jest z listy klientow przez zajety nickname to wiadomosc powinno isc tylko do niego (a idzie do wszystkich REMOVE a do niego NICK_TAKEN)
// do tego nie jest ustawiany jego nickname - fix bo contents dostaje NONE

int epoll_fd;

void Client::waitForWrite(bool epollout) {
        epoll_event ee {EPOLLIN | EPOLLRDHUP | (epollout == true ? EPOLLOUT : 0), {.ptr = this}};
        epoll_ctl(epoll_fd, EPOLL_CTL_MOD, m_socket, &ee);
}

Client::Client(int socket, sockaddr_in client_address) : Handler(socket)
{
    epoll_event ee {EPOLLIN | EPOLLRDHUP, {.ptr=this}};
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
    std::cout << currentConnectionInfo() << " Removing connection" << std::endl;
    s_clients.erase(this);
    epoll_ctl(epoll_fd, EPOLL_CTL_DEL, m_socket, nullptr);
    shutdown(m_socket, SHUT_RDWR);
    close(m_socket);
}

void Client::setWords(const std::vector<std::string> &words)
{
   s_words = words;
}

std::string Client::currentConnectionInfo() const
{
    std::stringstream ss;
    ss << "[" << inet_ntoa(m_address.sin_addr) << ":" << ntohs(m_address.sin_port) << "]";
    return ss.str();
}

void Client::setIndex(const int index)
{
    s_index = index;
}

void Client::handleEvent(uint32_t events) 
{   
    if(events & EPOLLIN) {
        if(readBuffer.message_length_read)
        {
            ssize_t count = read(m_socket, readBuffer.dataCurrentPosition(), readBuffer.current_message_length);
            if(count <= 0)
                events |= EPOLLERR;
            else {
                // Read count bytes to position
                readBuffer.position += count;

                if(readBuffer.position == readBuffer.current_message_length)
                {
                    std::cout << currentConnectionInfo() << " Full message received" << std::endl;
                    // Got full message
                    MessageCode code = static_cast<MessageCode>(readBuffer.data[0] - '0');
                    std::string message_received{};

                    // Read message length bytes
                    for(int i = 1; i < readBuffer.current_message_length; i++)
                    {
                        message_received += readBuffer.data[i];
                    }

                    MessageBuilder message(code, message_received, readBuffer.current_message_length);
                    std::cout << currentConnectionInfo() << " Message received: " << std::endl;
                    std::cout << message << std::endl;

                    // Send message (add to queue)
                    handleReceivedMessage(message);

                    // Empty data buffer
                    readBuffer.current_message_length = 0;
                    readBuffer.position = 0;
                    readBuffer.message_length_read = false;
                }
            }   
        }
        else {
             // Proceed with normal read
            // Non blocking read for 2 bytes
            ssize_t count = read(m_socket, readBuffer.dataCurrentPosition(), 2);
            if(count <= 0)
                events |= EPOLLERR;
            else {
               
                readBuffer.position += count;

                // If read 2 bytes (message size) and message size was not setted yet
                if(readBuffer.position == 2 && !readBuffer.message_length_read)
                {
                    std::cout <<  currentConnectionInfo() << " Received incoming message length" << std::endl;
                    // Set message length
                    readBuffer.current_message_length = (readBuffer.data[0] - '0') * 10 + (readBuffer.data[1] - '0');
                    // Proceed to read after 2 bytes of message length
                    readBuffer.position = 0;
                    readBuffer.message_length_read = true;
                    
                }
            }
        }
    }

    // Event triggered by not sending full message
    if(events & EPOLLOUT) {   
        std::cout << currentConnectionInfo() << " Sending partial data" << std::endl;
        do {   
            // See what's left to send
            int remaining = dataToWrite.front().remaining();

            // Send what's left in non blocking mode
            int sent = send(m_socket, dataToWrite.front().data + dataToWrite.front().position, remaining, MSG_DONTWAIT);
            if(sent == remaining) {
                std::cout << currentConnectionInfo() << " Full message sent" << std::endl;
                dataToWrite.pop_front();
                if(dataToWrite.size() == 0) {
                    waitForWrite(false);
                    break;
                }
                continue;
            } else if (sent == -1) {
                if(errno != EWOULDBLOCK && errno != EAGAIN)
                    events |= EPOLLERR;
            } else {
                dataToWrite.front().position += sent;
            }
        } while(false);
    }
   
    // Fatal error occured on client socket
    if(events & ~(EPOLLIN | EPOLLOUT)) {
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
    std::cout << this->currentConnectionInfo() << " sending message to: " << client->currentConnectionInfo() << std::endl;
    std::cout << message << std::endl;
    std::string messageToSend = message.serialize();
    int messageSize = messageToSend.size();

    // We have more messages being processed hence wait for them to finish
    if(dataToWrite.size() != 0) {
        dataToWrite.emplace_back(messageToSend.data(), messageSize);
        return;
    }

    // Non blockling send
    int sent = send(client->m_socket, messageToSend.data(), messageSize, MSG_DONTWAIT);
    if(sent == messageSize) {
        // Full message has been send
        std::cout << currentConnectionInfo() << " Full message sent (no queue)" << std::endl;
        return;
    }
    // Either message buffer blocked or fatal error
    if(sent == -1) {
        // Fatal error - remove connection
        if(errno != EWOULDBLOCK && errno != EAGAIN) {
            delete client;
            return;
        }

        std::cout << currentConnectionInfo() << " Message cannot be send hence placing it on the wait list" << std::endl;
        // Message failed send (ewouldblock == true || egain == true)
        // Place it back on buffer
        dataToWrite.emplace_back(messageToSend.data(), messageSize);
    } else {
        std::cout << currentConnectionInfo() << " Message send partially hence placing the rest on the wait list" << std::endl;
        // Message send but not fully hence send what's left
        dataToWrite.emplace_back(messageToSend.data() + sent, messageSize - sent);
    }
    std::cout << currentConnectionInfo() << " Waiting for write" << std::endl;
    waitForWrite(true);
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
            s_words[s_index],
            s_words[s_index].size()
        );

        sendToAll(ready);
    }
}

void Client::guessed_letter(const std::string &message)
{
    // Check for winner
    if(this->m_guessed == static_cast<int>(this->s_words[s_index].size()) && this->m_missed != MAX_GUESS)
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
        this->m_missed++;
    }
    else if(message[0] == '1')
    {
        this->m_missed++;
    }  
    
    // Update all clients with ranking
    // nick:{trafione}:{nietrafione}

    std::string response = this->m_nickname +":" +std::to_string(this->m_guessed) + ":" + std::to_string(this->m_missed);
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
                std::cout << currentConnectionInfo() << "Invalid nickname - duplicate: " << nickname << std::endl;
                // MessageBuilder::Info info(MessageBuilder::NICK_TAKEN, "taken");
                MessageBuilder info(
                    MessageCode::NICK_TAKEN
                );

                sendToOne(this, info);
                // to cie wykurwia z bazy calkowicie i wysyla wiadomosc o remove do reszty
                delete this;
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