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
#include <sstream>

const std::vector<std::string> words{
	"ala ma kota",
	"super serwer",
	"michal to debil",
	"leniwa kurwa"
};

static std::random_device rd;
static std::mt19937 engine(rd());
static std::uniform_int_distribution<int> distribute(0, words.size() - 1);

enum class Code
{
	NEW_HOST = 1,
	NEW_PLAYER,
	READY,
	GUESSED_RIGHT, 
	WINNER,
	RECONNECT,
	NEW_PASSWORD,
};

struct Client
{
	int m_fd;
	std::string m_nickname{};
	static int new_player_id;
	int player_id;
	int m_guessed = 0;
	int m_missed = 0;
	bool is_host = false;

	Client(int fd, const std::string &nickname) : m_nickname(nickname), m_fd(fd) 
	{
		player_id = new_player_id++;
	}
};

int Client::new_player_id = 0;

int word_index = -1;

std::vector<Client*> clients{};


// std::vector<int> (id, punkty)
// Client - status, nickname, id

int check(int expected, const std::string &message, int compare = -1)
{
	if(expected == compare) {
		perror(message.c_str());
		exit(1);
	}
	return expected;
}

void new_host(int &client_socket, const std::string &data)
{
	std::cout << "new_host start" << std::endl;
	// DATA TO CALA WIADOMOSC
	word_index = distribute(engine);
	std::cout << "generated" << std::endl;
	Client *client = new Client(client_socket, data);
	client->is_host = true;
	std::cout << client->new_player_id << std::endl;
	clients.emplace_back();
	std::cout << "new client created" << std::endl;

	std::string message_to_host = std::to_string(static_cast<int>(Code::NEW_PASSWORD)) +
		words[word_index] + std::to_string(client->player_id);
	int length = message_to_host.length();
	if(length <= 9) {
		message_to_host = '0' + std::to_string(length) + message_to_host;
	}
	message_to_host = std::to_string(length) + message_to_host;
	std::cout << "message constructed" << std::endl;
	if(send(client_socket, message_to_host.data(), message_to_host.length(), 0) == -1)
	{
		std::cerr << "Send failed" << std::endl;
		return;
	}
	std::cout << "message sended" << std::endl;
}

void invalid_nickname(int client_socket)
{
	static const std::string return_message{"taken1"};
	if(send(client_socket, return_message.data(), return_message.size(), 0) > 0) {
		return;
	}
	std::cerr << "Send to failed - invalid nickname handler" << std::endl;
}

void valid_player(Client *client)
{	
	std::string return_message = "7" + words[word_index] + std::to_string(client->player_id);
	if(send(client->m_fd, return_message.data(), return_message.size(), 0) > 0) {
		return;
	} 
	std::cerr << "Valid player send error";
}

void new_player(int client_socket, std::string &nickname)
{
	// Data -> nickname
	for(const auto client : clients) {
		// Causes segmentation fault
		if(client->m_nickname == nickname) {
			// Send error back to client
			std::cout << "Found player with the same nickname: " << client->m_nickname << std::endl;
			invalid_nickname(client_socket);
			return;
		}
	}

	// Add new player
	Client *client = new Client(client_socket, nickname);
	std::cout << "New player: id: " << client->player_id << std::endl;
	clients.emplace_back(client);

	// Send information back to player
	valid_player(client);
}



std::string checkForNickname(int client_socket, std::string &data)
{
	return std::string();
}

void handle_connection(int client_socket)
{
	while(true)
	{
		// Blocking read to get size of the whole message (2 bytes max)
		std::string message_size;
		if(recv(client_socket, message_size.data(), 2, MSG_WAITALL) != 2)
		{
			std::cerr<< "Received failed" << std::endl;
			break;
		}
		int message_size_int = std::stoi(message_size);
		std::cout << message_size_int << std::endl;
		std::string data(message_size_int, '*');
		if(recv(client_socket, data.data(), message_size_int, MSG_WAITALL) != message_size_int)
		{
			std::cerr << "Received failed" << std::endl;
			break;
		}
		std::cout << "Received: " << message_size_int << " bytes: " << data << std::endl;

		// 40 - wielkosc nazwy uzytkownika bez \0 + 1 bo kod wiadomosci + 2 hasztagi

		// data[0] - kod wiadomosci
		// data[1] - #

		// data[len] - #

		Code message_code = static_cast<Code>(data[0] - '0');
		std::cout << "Error code: " << static_cast<int>(message_code) << std::endl;
		std::string message = data.erase(0, 1);
		std::cout << "Message: " << message << " [" << message.length() << "]" << std::endl;
		switch(message_code)
		{
			case Code::NEW_HOST:
				std::cout << "NEW_HOST" << std::endl;
				new_host(client_socket, message);
				break;
			case Code::NEW_PLAYER:
				std::cout << "NEW PLAYER" << std::endl;
				new_player(client_socket, message);
				break;
			case Code::READY:
				std::cout << "READY" << std::endl;
				break;
			case Code::GUESSED_RIGHT:
				std::cout << "GUESSED_RIGHT" << std::endl;
				break;
			case Code::NEW_PASSWORD:
				std::cout << "NEW_PASSWORD" << std::endl;
				break;
			case Code::RECONNECT:
				std::cout << "RECONNECT" << std::endl;
				break;
			case Code::WINNER:
				std::cout << "WINNER" << std::endl;
				break;
			default:
				std::cerr << "ERROR: invalid message code" << std::endl;
				break;
		}
		
		// Dummy send
		// write(client_socket, "12345", 6);
	}

	close(client_socket);
}

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
	check(listen(server_socket, SOMAXCONN), "Listen failed");
	std::cout << "Listening with max backlog: " << SOMAXCONN << std::endl;

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


