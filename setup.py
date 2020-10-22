from distutils.command.build_ext import build_ext
from distutils.core import setup, Extension
import os
import shutil
import command as cmd

# monero src/damon object compile options
LIST_CPP_INCLUDE_DIRS = ['/usr/local/include','./external/rapidjson/include','./external/easylogging++','./src','./contrib/epee/include','./external','./external/supercop/include','./build/debug/generated_include','./build/debug/translations','./external/db_drivers/liblmdb','./external/miniupnp/miniupnpc/']
LIST_CPP_MACROS = [('AUTO_INITIALIZE_EASYLOGGINGPP',None),('BLOCKCHAIN_DB','DB_LMDB'),('BUILD_SHARED_LIBS',None),('DEFAULT_DB_TYPE','lmdb'),('DEVICE_TREZOR_READY','1'),('HAVE_EXPLICIT_BZERO',None),('HAVE_READLINE',None),('HAVE_STRPTIME',None),('MINIUPNP_STATICLIB',None),('PER_BLOCK_CHECKPOINT',None),('PROTOBUF_INLINE_NOT_IN_HEADERS','0'),('STACK_TRACE',None),('TREZOR_DEBUG','1'),('_GNU_SOURCE',None)]  #default define in ubuntu ['_FORTIFY_SOURCE=2' ]
LIST_CC1_EXTRA_CLANG = ['-std=c++11', '-ftemplate-depth=900']
LIST_CC1_EXTRA_OPT = ['-fstack-protector','-Og'] #default define ['-fstack-protector-strong','-fno-strict-aliasing']
LIST_CC1_EXTRA_DEBUG = ['-g3'] #default define ['-g']
LIST_CC1_EXTRA_CODEGENERATION = [''] #default define ['-fPIC']
LIST_CC1_EXTRA_WARNING = ['-Wall','-Wextra','-Wpointer-arith','-Wundef','-Wvla','-Wwrite-strings','-Wno-missing-field-initializers','-Wlogical-op'] #default define in ubuntu(>= 8.10) ['-Wformat','-Wformat-security', '-Wdate-time']
LIST_CC1_EXTRA_SPECIFIC_WARNING = ['-Wno-error=extra','-Wno-error=deprecated-declarations','-Wno-error=unused-variable','-Wno-error=undef','-Wno-error=maybe-uninitialized','-Wno-error=cpp','-Wno-error=uninitialized','-Wno-unused-parameter','-Wno-unused-variable','-Wno-reorder']
LIST_AS_EXTRA_MACHINE = ['-march=native','-maes','-mmitigate-rop']  #default define ['-pthread']
#LIST_LD_EXTRA_LINKER = ['-shared']
WD = os.getcwd()
LIBPAHTS = WD+"/build/temp.linux-x86_64-2.7/libs"

def exec_shell_cmd(cmd):
    if os.system(cmd) != 0:
        print("error while executing '%s'" % cmd)
        exit(-1)

def install_files(lists):
    for li in lists:
        path = os.path.split(li)
        if os.path.isfile(li):
            shutil.copy(li, LIBPAHTS+"/"+path[1])

def create_external_libs():
    # external libs are consist of subtrees('db_drivers','easylogging++'), submodues('unbound','miniupnp/miniupnpc','randomx') and the source code('rapidjson','trezor-common') used only for include   
    modules = ['unbound','db_drivers','easylogging++','miniupnp/miniupnpc']      
    for module in modules:
        print("---------------------------------")
        print(" Start compile ...  -  %s  - " %(module))
        print("---------------------------------")
        if module!='unbound':
            if os.path.exists(WD+"/external/"+module+"/build"):
                exec_shell_cmd("cd %s/%s && cd build && cmake .. && make" % (WD+"/external", module))
            else:
                exec_shell_cmd("cd %s/%s && mkdir build && cd build && cmake .. && make" % (WD+"/external", module))  
        else:
            exec_shell_cmd("cd %s/%s && ./configure && make" % (WD+"/external", module))            

    lists = ["./external/unbound/.libs/libunbound.so","./external/db_drivers/build/liblmdb/liblmdb.so","./external/easylogging++/build/libeasylogging.so","./external/randomx/build/librandomx.so","./external/miniupnp/miniupnpc/build/libminiupnpc.a"]
    install_files(lists)

def create_static_libs():
    print("----------------------------------------------------------------------------")
    list_txt = ['epee.txt', 'blocks.txt','epee_readline.txt']
    for i in range(0,len(list_txt)):
        print("static-lib : -  %s   -  start compile ... " %(list_txt[i]))
        target = "static_txt/" + list_txt[i]
        f = open(target,"r")
        while True:
            line = f.readline()
            if not line : break
            exec_shell_cmd(line)    
        f.close()
    print(" Successfully ... ")
    print("----------------------------------------------------------------------------")

def create_six_objects():
    print("----------------------------------------------------------------------------")
    print(" Start compile ...  6 objects ")
    target = "static_txt/monerod_objects.txt"
    f = open(target,"r")
    while True:
        line = f.readline()
        if not line : break
        exec_shell_cmd(line)    
    f.close()
    print(" Successfully ... ")
    print("----------------------------------------------------------------------------")

def create_randomx():
    print("----------------------------------------------------------------------------")
    print(" Start compile ... external librandomx.so.")
    target = "static_txt/randomx.txt"
    f = open(target,"r")
    while True:
        line = f.readline()
        if not line : break
        exec_shell_cmd(line)    
    f.close()
    print(" Successfully ... ")
    print("----------------------------------------------------------------------------")


def create_shared_libs():    
    # In monerod, a total of 24 shared libraries are linked, 4 of which were previously installed as external libs.
    # And certain shared libs link 3 static libs, but they are pre-installed in the'creaste_external_libs' step.
    # In addition Monerod in not linked to "libdaemon_messagesd.so", but added because "libdaemon_rpc_serverd.so" linked by monerod links "libdaemon_messagesd.so".
    # Be careful with the build order of your modules, because there are links between modules.

    # modules = ['/src','/src/hardforks','/src/crypto','/src/common','/src/ringct/libringct_basicd.so','/src/checkpoints','/src/net','/src/rpc/librpc_based.so','/src/daemonizer','/src/device','/src/cryptonote_basic','/src/ringct/libringctd.so','/src/multisig','/src/blockchain_db','/src/cryptonote_core','/src/p2p','/src/cryptonote_protocol','/src/rpc/librpcd.so','/src/serializat','/src/rpc/libdaemon_messagesd.so','/src/rpc/libdaemon_rpc_serverd.so'] # Number of modules : 21 (24-4+1=21)
    
    modules = ['libversion','/src/hardforks','/src/crypto','/src/common','/src/ringct/libringct_basicd.so','/src/checkpoints','/src/net','/src/rpc/librpc_based.so'] #15
    #modules2 = ['/src/ringct/libringct_basicd.so','/src/rpc/librpc_based.so','/src/ringct/libringctd.so','/src/rpc/librpcd.so','/src/rpc/libdaemon_messagesd.so','/src/rpc/libdaemon_rpc_serverd.so'] # 6
    for module in modules:
        size = len(module.split('.')) 
        if size > 1:
            #print(module.split('.')[1])
            pth = os.path.split(module)[0]
            name = os.path.split(module)[1]
            if os.path.exists(WD+pth+"/build"):
                exec_shell_cmd("cd %s && cd build && cmake .. && make" % (WD+pth))                
            else:
                exec_shell_cmd("cd %s && mkdir build && cd build && cmake .. && make" % (WD+pth))             
        else:
            #print(text.split('.')[0])        
            if module =='libversion':
                if os.path.exists(WD+"/build"):
                    exec_shell_cmd("cd %s && cd build && cmake .. && make" % (WD))
                else:
                    exec_shell_cmd("cd %s && mkdir build && cd build && cmake .. && make" % (WD))
            else:
                if os.path.exists(WD+module+"/build"):
                    exec_shell_cmd("cd %s && cd build && cmake .. && make" % (WD+module))                
                else:
                    exec_shell_cmd("cd %s && mkdir build && cd build && cmake .. && make" % (WD+module))            

def cmd_ex(command_subclass):
    orig_ext = command_subclass.build_extension
    def build_ext(self, ext):
        # First, create 6 object files that make up monerod.
        # I made a custom version of "python3-distutils" and used it to understand the compilation options.
        # python3-distutils and python3 are in the default Ubuntu 18.04 repositories
        # This step is executed before the main function when executed with'python setup.py build'.
        
        sources = self.swig_sources(list(ext.sources), ext)
        extra_args = ext.extra_compile_args or []
        macros = ext.define_macros[:]
        for undef in ext.undef_macros:
            macros.append((undef,))

        objects = self.compiler.compile(sources,
                                        output_dir=self.build_temp,
                                        #output_dir=obj_path,
                                        macros=macros,
                                        include_dirs=ext.include_dirs,
                                        debug=self.debug,
                                        extra_postargs=extra_args,
                                        depends=ext.depends)
        self._built_objects = objects[:]
        if ext.extra_objects:
            objects.extend(ext.extra_objects)
        extra_args = ext.extra_link_args or []

    command_subclass.build_extension = build_ext
    return command_subclass

# ----------------------------------------------------------------------------------
# setup (name = 'ObjectFiles',
#        version = '1.0',
#        description = 'Monero Damon Object Files',
#        author = 'Victork',
#        cmdclass = {'build_ext': build_ext_ex},
#        ext_modules = [object1,object2,object3,object4,object5,object6])
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------
# python shell           : exec_shell_cmd("cd %s && " % (WD))
# Install path           : ./build/temp.linux-x86_64-2.7/libs/

# object code ----------------------------------------------------------------------------------
# 1.delete                      : `cd /home/mong/source/monero/build/Linux/master/debug/src/common && `
# 2.replace incldue path        : `/home/mong/source/monero` -> `.`
# 3.delete                      : `-I./build/Linux/master/debug/generated_include`
# 4.replace                     : `-I./build/Linux/master/debug/translations` -> `-I./src/translations`
# 5.replace object install path : `CMakeFiles/obj_common.dir` -> `source code location`

# shared object code ---------------------------------------------------------------------------
# 1.replace install path        : `-o *.so` -> `-o ./build/temp.linux-x86_64-2.7/libs/*.so`
# 2.replace object path         : `CMakeFiles/obj_common.dir` -> `source code location`
# 3.replace rpath               : `-Wl,-rpath,/home/victor/CLionProjects/~~~~` -> `-Wl,-rpath,/build/temp.linux-x86_64-2.7/libs`
# ----------------------------------------------------------------------------------

if __name__ == '__main__':
    print ("-------------------------------------------------------------")
    print ("To compile monerod, the following file needs to be created.\n--1.Creating Object Files(6)\n--2.Creating Dependent Static libraries(4)\n--3.Creating Shared libraries(25)")
    print ("-------------------------------------------------------------")
    exec_shell_cmd("git submodule update --init")
    if not os.path.exists(LIBPAHTS):
                exec_shell_cmd("cd %s && mkdir -p %s" % (WD, LIBPAHTS))
    create_randomx()
    create_six_objects()
    create_external_libs()
    create_static_libs()    

    cmd.gcc_command03("3.libversion.so")
    cmd.gcc_command04("4.libhardforksd.so")
    cmd.gcc_command05("5.libcncryptod.so")
    cmd.gcc_command06("6.libcommond.so") # transaction.h 
    cmd.gcc_command07("7.libringct_basicd.so")
    cmd.gcc_command08("8.libcheckpointsd.so")
    cmd.gcc_command09("9.libnetd.so")
    cmd.gcc_command10("10.librpc_based.so")
    cmd.gcc_command11("11.libdaemonizerd.so")
    cmd.gcc_command12("12.libdeviced.so")    #------------------------> object 2, not existed
    cmd.gcc_command13("13.libcryptonote_basicd.so")   #rpath-link : 
    cmd.gcc_command14("14.libringctd.so")
    cmd.gcc_command15("15.libmultisigd.so")
    cmd.gcc_command16("16.libblockchain_dbd.so")
    cmd.gcc_command17("17.libcryptonote_cored.so")
    cmd.gcc_command18("18.libp2pd.so")
    cmd.gcc_command19("19.libcryptonote_protocold.so")
    cmd.gcc_command20("20.librpcd.so")
    cmd.gcc_command21("21.libserializationd.so")
    cmd.gcc_command22("22.libdaemon_messagesd.so")
    cmd.gcc_command23("23.libdaemon_rpc_serverd.so")
    cmd.gcc_command_monero("libmonerod.so")


      







