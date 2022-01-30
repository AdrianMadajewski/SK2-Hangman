#include "Utility.h"

int server_socket;

void error(const std::string &message, ErrorCode error)
{
    switch(error)
    {
        case FAILURE:
            perror(message.c_str());
            break;
        case FATAL:
            perror(message.c_str());
            exit(1);
            break;
        case UNKNOWN:  
            std::cerr << "Unkwnon error" << std::endl;
            break;
        default: 
            std::cerr << "Lorem ipsum..." << std::endl;
            break;
    }
}

void setReuseAddress(int socket)
{
    static const int one = 1;
    int result = setsockopt(socket, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one));
    if(result) error("[SERVER]: Reuse address control failed", ErrorCode::FATAL);
}

uint16_t readPort(const char *string)
{
    char *end;
	auto port = strtol(string, &end, 10);
	if(*end != 0 || port < 1 || port > 65535)
	{
		error("[SERVER]: Illegal argument - port", ErrorCode::FATAL);
	}
    return port;
}

void ctrl_c(int)
{
    for(Client * client : Client::getClients())
    {
        delete client;
    }
    close(server_socket);
    printf("[SERVER]: Closing server\n");
    exit(0);
}

std::vector<std::string> getFileContents(const std::string &filename)
{
    if (filename.empty()) {
		std::cerr << "[SERVER]: Ivalid filename" << std::endl;
		exit(1);
	}

	std::vector<std::string> data{};
	std::ifstream file;
	file.open(filename);

	if (!file.is_open()) {
		std::cerr << "[SERVER]: Couldn't find config file: " << filename << std::endl;
		exit(1);
	}
	else {
		std::cout << "[SERVER]: Succesfully read from file " << filename << std::endl;
		
		while (!file.eof()) {
			std::string string;
			file >> string;
			data.emplace_back(string);
		}
	}
	file.close();
	return data;
}