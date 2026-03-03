CXX = g++
CXXFLAGS = -std=c++20 -Wall -Wextra -O2
TARGET = output/program
OUTDIR = output
SRCS = $(wildcard *.cpp)
OBJS = $(SRCS:%.cpp=$(OUTDIR)/%.o)

.PHONY: run
run: $(TARGET)
	@echo "Running $(TARGET)..."
	@./$(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

$(OUTDIR)/%.o: %.cpp | $(OUTDIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(OUTDIR):
	mkdir -p $(OUTDIR)

.PHONY: clean
clean:
	rm -rf $(OUTDIR)
