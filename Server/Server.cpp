#include "Server.h"

void ServerHandler::handleEvent(uint32_t events) {
     if(events & EPOLLIN) {
        sockaddr_in client_address{};
        socklen_t client_address_size = sizeof(client_address);

        int client_fd = accept(m_socket, (sockaddr*)&client_address, &client_address_size);
        if(client_fd == -1) error("Accept failed", ErrorCode::FATAL);

        Client *client = new Client(client_fd, client_address);

        std::cout << client->currentConnectionInfo() << " New connection established" << std::endl;
    }

    if(events & ~EPOLLIN) {
        error("Event " + std::to_string(events) + " on server socket");
        ctrl_c(SIGINT);
    }
 }

 void ServerHandler::ctrl_c(int)
{
    for(Client * client : Client::getClients())
        delete client;
    close(m_socket);
    printf("Closing server\n");
    exit(0);
}