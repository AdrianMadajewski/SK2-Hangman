#ifndef UTIL_H
#define UTIL_H

#include "Client.h"
#include "Server.h"

#include <sys/types.h>         
#include <sys/socket.h>
#include <unistd.h> 
#include <stdlib.h>     /* strtol */

#include <random>
#include <iostream>
#include <fstream>

enum ErrorCode
{
    UNKNOWN = -1,
    FATAL,
    FAILURE
};

namespace MyRandom
{
	static std::random_device rd;
	static std::mt19937 seed(rd());

	inline static int generateNumber(const int min, const int max)
	{
		std::uniform_int_distribution<> die{ min, max };
		return die(MyRandom::seed);
	}
}

void error(const std::string &message, ErrorCode error = ErrorCode::FAILURE);
void setReuseAddress(int socket);
void ctrl_c(const int, int server_socket);
uint16_t readPort(const char *string);
std::vector<std::string> getFileContents(const std::string &filename);

#endif