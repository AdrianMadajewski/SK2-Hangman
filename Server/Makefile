
FILES:=$(wildcard *.cpp)
FILENAME=server
FLAGS=--std=c++17 -Wall -Wextra

main_file: $(FILES) 
	g++ -g -o $(FILENAME) $(FILES) $(FLAGS);
run:
	./$(FILENAME) config.cfg
clean:
	rm $(FILENAME)
