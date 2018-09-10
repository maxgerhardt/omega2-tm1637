# C compiler
CC:= mipsel-openwrt-linux-g++
# path where the toolchain is
TOOLCHAIN_ROOT_DIR:= /home/max/source/staging_dir/target-mipsel_24kc_musl-1.1.16
#path where the omega_includes and omega_libs folder are
OMEGA_DIR:= /home/max/omega

# additional includes from toolchain
INCLUDE_DIRS:=$(TOOLCHAIN_ROOT_DIR)/usr/include
LIB_DIRS:=$(TOOLCHAIN_ROOT_DIR)/usr/lib

#links to link against
LDFLAGS_LIB:= -loniondebug -lugpio
LDFLAGS_PROGRAM = 
CFLAGS:= -O3 -ggdb -g -Wall -Wextra -std=c++14
IFLAGS:= -I $(INCLUDE_DIRS) -I $(OMEGA_DIR)/omega_includes

EXAMPLE_SOURCE = example_display
PROGRAM_SOURCES = $(EXAMPLE_SOURCE).cpp TM1637.cpp Arduino.cpp
EXECUTABLE:= tm1637_$(EXAMPLE_SOURCE)

export STAGING_DIR="$TOOLCHAIN_ROOT_DIR/staging_dir/"

.PHONY : program all clean all

program:
	$(CC) -o $(EXECUTABLE) $(CFLAGS) $(IFLAGS) -L $(LIB_DIRS) -L $(OMEGA_DIR)/omega_libs -L. $(PROGRAM_SOURCES) $(LDFLAGS_PROGRAM) $(LDFLAGS_LIB)

all: | program

upload: | all
	sshpass -p "onioneer" scp $(EXECUTABLE) root@192.168.1.202:/root/.

clean:
	rm -rf $(EXECUTABLE)
	rm -rf $(LIB_NAME)
