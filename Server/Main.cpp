#include "MessageBuilder.h"
#include "Client.h"
#include "Utility.h"
#include "Server.h"

#include <error.h>
#include <errno.h>
#include <signal.h> // SIGINT

extern int epoll_fd;

// ZROB SOBIE MAKEFILE CIOTO #ten mądry zrobił

int main(int argc, char **argv)
{
    if(argc != 2) 
    {
        std::cout << "Usage: " + std::string(argv[0]) + " <port>" << std::endl;
        exit(1);
    }
    long server_port = readPort(argv[1]);
    std::cout << "Port assigned succesfully: " << server_port << std::endl;

    int server_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if(server_socket == -1) error("Server socket initial failure", ErrorCode::FATAL);

    setReuseAddress(server_socket);

    // Set sigint to call ctrl_c as a handler
    signal(SIGINT, (void(*)(int))ctrl_c);

    // Ignore sigpipe signal
    signal(SIGPIPE, SIG_IGN);

    std::cout << "Server socket created with initalized settings" << std::endl;

    // INADDR ANY TRZEBA BEDZIE ZMIENIC NA DOWOLNY ADRES

    sockaddr_in server_addr {
        .sin_family=AF_INET,
        .sin_port=htons((short)(server_port)),
        .sin_addr={INADDR_ANY}
    };

    int err = bind(server_socket, (sockaddr*)&server_addr, sizeof(server_addr));
    if(err) error("Bind socket failed", ErrorCode::FATAL);

    std::cout << "Server socket binded" << std::endl;

    const int LISTEN_CAP = 1;
    err = listen(server_socket, 1);
    if(err) error("Listen failed", ErrorCode::FATAL);

    std::cout << "Listening for events with capacity: " << LISTEN_CAP << std::endl;

    ServerHandler server(server_socket);

    epoll_fd = epoll_create1(0);
    epoll_event ee {EPOLLIN, {.ptr = &server}};
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, server_socket, &ee);

    std::cout << "Epoll initalized - server added to epoll-fd" << std::endl;

    while(true) {
        std::cout << "Waiting for event..." << std::endl; 
        // Epoll wait max 1 event -1 timeout (infinite)
        if(epoll_wait(epoll_fd, &ee, 1, -1) == -1) {
            ::error(0, errno, "epoll_wait failed");
            ctrl_c(SIGINT, server_socket);
        }

        ((Handler*)ee.data.ptr)->handleEvent(ee.events);
    }

    return 0;
}