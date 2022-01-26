#ifndef HANDLER_H
#define HANDLER_H

#include <inttypes.h>

class Handler
{
protected:
    int m_socket;
public:
    virtual ~Handler() {}
    virtual void handleEvent(uint32_t events) = 0;
    Handler(int socket) : m_socket(socket) {}
    int getSocket() { return m_socket; }
};

#endif