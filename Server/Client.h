#ifndef CLIENT_H
#define CLIENT_H

#define RESET_CODE "7"

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
#include <map>
#include <pthread.h>
#include <fstream>
#include <unordered_set>
#include <string>

const std::vector<std::string> words = {
    "politechnika",
    "debil"
};

std::string global_word;

namespace random
{
	std::random_device rd;
	std::mt19937 seed(rd());

	int generateNumber(const int min, const int max)
	{
		std::uniform_int_distribution<> die{ min, max };
		return die(random::seed);
	}
}

void error(const std::string &message)
{
    perror(message.c_str());
}

class Client
{
public:
    Client(int socket, const std::string nickname);
    virtual ~Client();
    static void sendToOne(Client *client, const std::string &message);
    static void sendToAll(const std::string &message);
    bool host_ready();
    static bool reset();
    static void setNewWord();
    static std::unordered_set<Client*> getClients();
    static void newPlayer(int socket, const std::string &nickname);
private:
    inline static int s_id = 0;
    int m_socket;
    int m_id;
    int m_guessed;
    int m_missed;
    bool m_host;
    std::string m_nickname;
    static std::unordered_set<Client*> s_clients;
    static std::string s_word;
};


#endif;