#include "Server.h"

void ServerHandler::handleEvent(uint32_t events) {
     if(events & EPOLLIN) {
        sockaddr_in client_address{};
        socklen_t client_address_size = sizeof(client_address);

        int client_fd = accept(m_socket, (sockaddr*)&client_address, &client_address_size);
        if(client_fd == -1) error("Accept failed", ErrorCode::FATAL);

        std::cout << "New connection from: " << 
            inet_ntoa(client_address.sin_addr) << ":" << ntohs(client_address.sin_port) <<
            " (fd: " << client_fd << ")" << std::endl;
            

        // Oddajemy sterowanie do poszczegolnych klientow
        Client *client = new Client(client_fd, client_address);

        // delete client usuwa od razu klienta z listy klientow (jego destruktor robi to samo)
    }

    if(events & ~EPOLLIN) {
        error("Event " + std::to_string(events) + " on server socket");
        ctrl_c(m_socket);
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