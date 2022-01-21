#include <iostream>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <netdb.h>
#include <thread>
#include <random>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <vector>

int check(int expected, const std::string &message, int compare = -1)
{
	if(expected == compare) {
		perror(message.c_str());
		exit(1);
	}
	return expected;
}

void handle_connection(int client_socket)
{
	while(true)
	{
		// Blocking read to get size of the whole message (2 bytes max)
		char buffer[16]{};
		
		// Read for 2 bytes - size of the message
		check(read(client_socket, buffer, 2), "Read from client failed");
		int message_size = atoi(buffer);

		std::cout << "Got message size: " << message_size << std::endl;

		// Read 1 byte for message code
		memset(buffer, 0, sizeof(buffer));
		check(read(client_socket, buffer, 1), "Read from client failed");
		int message_code = atoi(buffer);

		std::cout << "Got message code: " << message_code << std::endl;

		

		// Dummy send
		// write(client_socket, "12345", 6);
	}
}

const std::vector<std::string> words{
	"ala ma kota",
	"super serwer",
	"michal to debil",
	"leniwa kurwa"
};

const int SERVER_BACKLOG = 1;

typedef struct sockaddr_in SA_IN;
typedef struct sockaddr SA;

int main(int argc, char **argv)
{
	if(argc != 3)
	{
		std::cout << "Usage: <ip> <port>" << std::endl;
		return 1; 
	}

	in_addr addr;
	if(!inet_aton(argv[1], &addr))
	{
		std::cerr << "Invalid ip address: " << argv[1] << std::endl;
		return 1;
	}

	char *end;
	long port = strtol(argv[2], &end, 10);
	if(*end != 0 || port < 1 || port > 65535)
	{
		std::cerr << "Invalid port number: " << argv[2] << std::endl;
		return 1;
	}

	addrinfo hints {
		.ai_flags=AI_PASSIVE,
		.ai_protocol=IPPROTO_TCP
	};
	addrinfo *resolved;
	if(int error_code = getaddrinfo(argv[1], argv[2], &hints, &resolved)) {
		std::cerr << "Resolving address failed: " << gai_strerror(error_code) << std::endl;
		return 1;
	}

	int server_socket;
	SA_IN server_addr;

	check((server_socket = socket(resolved->ai_family, resolved->ai_socktype, resolved->ai_protocol)), 
		"Failed to create socket");
	const int one = 1;
	check(setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one)), "Invalid options specified in socket");
	std::cout << "Socket created succesfully" << std::endl;

	// Initialize address structure
	server_addr.sin_family = AF_INET;
	server_addr.sin_addr.s_addr = INADDR_ANY;
	server_addr.sin_port = htons(atoi(argv[2]));

	check(bind(server_socket, resolved->ai_addr, resolved->ai_addrlen),
		"Bind failed");
	std::cout << "Binded socket to address: " << argv[1] << " on port: " << argv[2] << std::endl;

	freeaddrinfo(resolved);
	check(listen(server_socket, SERVER_BACKLOG), "Listen failed");
	std::cout << "Listening with max backlog: " << SERVER_BACKLOG << std::endl;

	while(true)
	{
		std::cout << "Waiting for connection" << std::endl;
		
		// New connection arrived
		int client_socket;
		SA_IN client_address;
		int addr_size = sizeof(client_address);
		check((client_socket = accept(
			server_socket, (SA*)&client_address, (socklen_t*)&addr_size
		)), "Accept failed");

		char buffer[INET_ADDRSTRLEN]{};
		if(!inet_ntop(AF_INET, &(client_address.sin_addr), buffer, INET_ADDRSTRLEN))
		{
			std::cerr << "Could not resolve client address" << std::endl;
			std::cerr << "Skipping" << std::endl;
		}

		std::cout << "Connection from: " << buffer << std::endl;
		handle_connection(client_socket);
	}

	close(server_socket);
	shutdown(server_socket, SHUT_RDWR);
	return 0;
}
