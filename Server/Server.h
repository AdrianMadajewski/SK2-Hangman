#ifndef SERVER_H
#define SERVER_H

#include "Handler.h"
#include "Utility.h"
#include "Client.h"

#include <iostream>
#include <string>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/epoll.h>
#include <signal.h>

class ServerHandler : public Handler
{
public:
    virtual void handleEvent(uint32_t events) override;
    void ctrl_c(int);
    ServerHandler(int socket) : Handler(socket) {}
};

#endif