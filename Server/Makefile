
FILES:=$(wildcard *.cpp)
FILENAME=server
FLAGS=--std=c++17

main_file: $(FILES) 
	g++ -g -o $(FILENAME) $(FILES) $(FLAGS);
run:
	./$(FILENAME)
clean:
	rm $(FILENAME)
compile: $(FILES) 
	g++ -o -g $(FILENAME) $(FILES) $(FLAGS)