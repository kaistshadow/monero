# Copyright (c) 2014-2019, The Monero Project
# 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this list of
#    conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice, this list
#    of conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors may be
#    used to endorse or promote products derived from this software without specific
#    prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

include_directories(../../../external/rapidjson/include ../../../external/easylogging++ ../../../src ../../../contrib/epee/include external)
list(INSERT CMAKE_MODULE_PATH 0
  "${CMAKE_SOURCE_DIR}/../../../cmake")
option(USE_READLINE "Build with GNU readline support." ON)
if(USE_READLINE AND NOT DEPENDS)
  find_package(Readline)
  if(READLINE_FOUND AND GNU_READLINE_FOUND)
    add_definitions(-DHAVE_READLINE)
    include_directories(${Readline_INCLUDE_DIR})
    message(STATUS "Found readline library at: ${Readline_ROOT_DIR}")
    set(EPEE_READLINE epee_readline)
  else()
    message(STATUS "Could not find GNU readline library so building without readline support")
  endif()
elseif(USE_READLINE AND DEPENDS AND NOT MINGW)
  find_path(Readline_INCLUDE_PATH readline/readline.h)
  find_library(Readline_LIBRARY readline)
  find_library(Terminfo_LIBRARY tinfo)
  set(Readline_LIBRARY "${Readline_LIBRARY};${Terminfo_LIBRARY}")
  set(GNU_READLINE_LIBRARY ${Readline_LIBRARY})
  add_definitions(-DHAVE_READLINE)
  set(EPEE_READLINE epee_readline)
endif()

add_library(epee STATIC byte_slice.cpp byte_stream.cpp hex.cpp abstract_http_client.cpp http_auth.cpp mlog.cpp net_helper.cpp net_utils_base.cpp string_tools.cpp
    wipeable_string.cpp levin_base.cpp memwipe.c connection_basic.cpp network_throttle.cpp network_throttle-detail.cpp mlocker.cpp buffer.cpp net_ssl.cpp
    int-util.cpp)

if (USE_READLINE AND (GNU_READLINE_FOUND OR (DEPENDS AND NOT MINGW)))
  add_library(epee_readline STATIC readline_buffer.cpp)
endif()

if(HAVE_C11)
SET_PROPERTY(SOURCE memwipe.c PROPERTY COMPILE_FLAGS -std=c11)
endif()

# Build and install libepee if we're building for GUI
if (BUILD_GUI_DEPS)
    if(IOS)
        set(lib_folder lib-${ARCH})
    else()
        set(lib_folder lib)
    endif()
    install(TARGETS epee
        ARCHIVE DESTINATION ${lib_folder})
    if (USE_READLINE AND GNU_READLINE_FOUND)
      install(TARGETS epee_readline
          ARCHIVE DESTINATION ${lib_folder})
    endif()
endif()

target_link_libraries(epee
  PUBLIC
    easylogging
    ${Boost_CHRONO_LIBRARY}
    ${Boost_FILESYSTEM_LIBRARY}
    ${Boost_THREAD_LIBRARY}
  PRIVATE
    ${OPENSSL_LIBRARIES}
    ${EXTRA_LIBRARIES})

if (USE_READLINE AND (GNU_READLINE_FOUND OR (DEPENDS AND NOT MINGW)))
  target_link_libraries(epee_readline
    PUBLIC
      easylogging
    PRIVATE
    ${GNU_READLINE_LIBRARY})
endif()
