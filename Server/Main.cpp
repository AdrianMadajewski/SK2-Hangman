#include "MessageBuilder.h"
#include "Client.h"
#include "Utility.h"
#include "Server.h"

#include <error.h>
#include <errno.h>
#include <signal.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/epoll.h>
#include <signal.h>
#include <unistd.h>
#include <fcntl.h>

extern int epoll_fd;
extern int server_socket;

int main(int argc, char **argv)
{
    if(argc != 2) 
    {
        std::cout << "Usage: " + std::string(argv[0]) + " <config.cfg>" << std::endl;
        return 1;
    }

    std::vector<std::string> config = getFileContents(std::string(argv[1]));

    long server_port = readPort(config[1].c_str());
    server_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if(server_socket == -1) error("Server socket initial failure", ErrorCode::FATAL);
    setReuseAddress(server_socket);

    
    // Ignore sigpipe signal
    signal(SIGPIPE, SIG_IGN);
     // Set sigint to call ctrl_c as a handler
    signal(SIGINT, ctrl_c);
   

    std::cout << "[SERVER]: Server socket created with initalized settings" << std::endl;

    // Zero initialize server_addr
    sockaddr_in server_addr {};
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons((short)(server_port));
    server_addr.sin_addr.s_addr = inet_addr(config[0].c_str());

    int err = bind(server_socket, (sockaddr*)&server_addr, sizeof(server_addr));
    if(err) error("[SERVER]: Bind socket failed", ErrorCode::FATAL);

    std::cout << "[SERVER]: Port assigned succesfully: " << server_port << std::endl;
    std::cout << "[SERVER]: Server socket binded" << std::endl;

    // Add files
    std::vector<std::string> words = getFileContents(config[2]);

    // Set statics
    Client::setWords(words);
    Client::setIndex(MyRandom::generateNumber(0, words.size()));
    
    std::cout << "[SERVER]: Random word set" << std::endl; 

    const int LISTEN_CAP = 1;
    err = listen(server_socket, 1);
    if(err) error("Listen failed", ErrorCode::FATAL);

    std::cout << "[SERVER]: Listening for events with capacity: " << LISTEN_CAP << std::endl;

    ServerHandler server(server_socket);

    epoll_fd = epoll_create1(0);
    epoll_event ee {EPOLLIN, {.ptr = &server}};
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, server_socket, &ee);

    std::cout << "[SERVER]: Epoll initalized - server added to epoll-fd" << std::endl; 

    while(true) {
        // Epoll wait max 1 event -1 timeout (infinite)
        std::cout << "[SERVER]: Waiting for event..." << std::endl;

        if(epoll_wait(epoll_fd, &ee, 1, -1) == -1 && errno != EINTR ) {
            ::error(0, errno, "Epoll wait failed");
            ctrl_c(SIGINT);
        }

        ((Handler*)ee.data.ptr)->handleEvent(ee.events);
    }

    return 0;
}