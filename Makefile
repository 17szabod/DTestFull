# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.23

# Default target executed when no arguments are given to make.
default_target: all
.PHONY : default_target

# Allow only one "make -f Makefile2" at a time, but pass parallelism.
.NOTPARALLEL:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /home/dani/.local/share/JetBrains/Toolbox/apps/CLion/ch-0/222.4345.21/bin/cmake/linux/bin/cmake

# The command to remove a file.
RM = /home/dani/.local/share/JetBrains/Toolbox/apps/CLion/ch-0/222.4345.21/bin/cmake/linux/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/dani/PycharmProjects/DTestFull

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/dani/PycharmProjects/DTestFull

#=============================================================================
# Targets provided globally by CMake.

# Special rule for the target edit_cache
edit_cache:
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --cyan "No interactive CMake dialog available..."
	/home/dani/.local/share/JetBrains/Toolbox/apps/CLion/ch-0/222.4345.21/bin/cmake/linux/bin/cmake -E echo No\ interactive\ CMake\ dialog\ available.
.PHONY : edit_cache

# Special rule for the target edit_cache
edit_cache/fast: edit_cache
.PHONY : edit_cache/fast

# Special rule for the target rebuild_cache
rebuild_cache:
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --cyan "Running CMake to regenerate build system..."
	/home/dani/.local/share/JetBrains/Toolbox/apps/CLion/ch-0/222.4345.21/bin/cmake/linux/bin/cmake --regenerate-during-build -S$(CMAKE_SOURCE_DIR) -B$(CMAKE_BINARY_DIR)
.PHONY : rebuild_cache

# Special rule for the target rebuild_cache
rebuild_cache/fast: rebuild_cache
.PHONY : rebuild_cache/fast

# The main all target
all: cmake_check_build_system
	$(CMAKE_COMMAND) -E cmake_progress_start /home/dani/PycharmProjects/DTestFull/CMakeFiles /home/dani/PycharmProjects/DTestFull//CMakeFiles/progress.marks
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 all
	$(CMAKE_COMMAND) -E cmake_progress_start /home/dani/PycharmProjects/DTestFull/CMakeFiles 0
.PHONY : all

# The main clean target
clean:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 clean
.PHONY : clean

# The main clean target
clean/fast: clean
.PHONY : clean/fast

# Prepare targets for installation.
preinstall: all
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 preinstall
.PHONY : preinstall

# Prepare targets for installation.
preinstall/fast:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 preinstall
.PHONY : preinstall/fast

# clear depends
depend:
	$(CMAKE_COMMAND) -S$(CMAKE_SOURCE_DIR) -B$(CMAKE_BINARY_DIR) --check-build-system CMakeFiles/Makefile.cmake 1
.PHONY : depend

#=============================================================================
# Target rules for targets named DTest

# Build rule for target.
DTest: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 DTest
.PHONY : DTest

# fast build rule for target.
DTest/fast:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/DTest.dir/build.make CMakeFiles/DTest.dir/build
.PHONY : DTest/fast

#=============================================================================
# Target rules for targets named PTemplate

# Build rule for target.
PTemplate: cmake_check_build_system
	$(MAKE) $(MAKESILENT) -f CMakeFiles/Makefile2 PTemplate
.PHONY : PTemplate

# fast build rule for target.
PTemplate/fast:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/PTemplate.dir/build.make CMakeFiles/PTemplate.dir/build
.PHONY : PTemplate/fast

src/DTest.o: src/DTest.c.o
.PHONY : src/DTest.o

# target to build an object file
src/DTest.c.o:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/DTest.dir/build.make CMakeFiles/DTest.dir/src/DTest.c.o
.PHONY : src/DTest.c.o

src/DTest.i: src/DTest.c.i
.PHONY : src/DTest.i

# target to preprocess a source file
src/DTest.c.i:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/DTest.dir/build.make CMakeFiles/DTest.dir/src/DTest.c.i
.PHONY : src/DTest.c.i

src/DTest.s: src/DTest.c.s
.PHONY : src/DTest.s

# target to generate assembly for a file
src/DTest.c.s:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/DTest.dir/build.make CMakeFiles/DTest.dir/src/DTest.c.s
.PHONY : src/DTest.c.s

src/PTemplate.o: src/PTemplate.c.o
.PHONY : src/PTemplate.o

# target to build an object file
src/PTemplate.c.o:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/PTemplate.dir/build.make CMakeFiles/PTemplate.dir/src/PTemplate.c.o
.PHONY : src/PTemplate.c.o

src/PTemplate.i: src/PTemplate.c.i
.PHONY : src/PTemplate.i

# target to preprocess a source file
src/PTemplate.c.i:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/PTemplate.dir/build.make CMakeFiles/PTemplate.dir/src/PTemplate.c.i
.PHONY : src/PTemplate.c.i

src/PTemplate.s: src/PTemplate.c.s
.PHONY : src/PTemplate.s

# target to generate assembly for a file
src/PTemplate.c.s:
	$(MAKE) $(MAKESILENT) -f CMakeFiles/PTemplate.dir/build.make CMakeFiles/PTemplate.dir/src/PTemplate.c.s
.PHONY : src/PTemplate.c.s

# Help Target
help:
	@echo "The following are some of the valid targets for this Makefile:"
	@echo "... all (the default if no target is provided)"
	@echo "... clean"
	@echo "... depend"
	@echo "... edit_cache"
	@echo "... rebuild_cache"
	@echo "... DTest"
	@echo "... PTemplate"
	@echo "... src/DTest.o"
	@echo "... src/DTest.i"
	@echo "... src/DTest.s"
	@echo "... src/PTemplate.o"
	@echo "... src/PTemplate.i"
	@echo "... src/PTemplate.s"
.PHONY : help



#=============================================================================
# Special targets to cleanup operation of make.

# Special rule to run CMake to check the build system integrity.
# No rule that depends on this can have commands that come from listfiles
# because they might be regenerated.
cmake_check_build_system:
	$(CMAKE_COMMAND) -S$(CMAKE_SOURCE_DIR) -B$(CMAKE_BINARY_DIR) --check-build-system CMakeFiles/Makefile.cmake 0
.PHONY : cmake_check_build_system

