from distutils.command.build_ext import build_ext
from distutils.core import setup, Extension
import os

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

def exec_shell_cmd(cmd):
    if os.system(cmd) != 0:
        print("error while executing '%s'" % cmd)
        exit(-1)

def create_external_libs():
    # external libs are consist of subtrees('db_drivers','easylogging++'), submodues('unbound','miniupnp/miniupnpc','randomx') and the source code('rapidjson','trezor-common') used only for include   
    modules = ['unbound','db_drivers','easylogging++','randomx','miniupnp/miniupnpc']      
    for module in modules:
        if module!='unbound':
            if os.path.exists(WD+"/external/"+module+"/build"):
                exec_shell_cmd("cd %s/%s && cd build && cmake .. && make" % (WD+"/external", module))
            else:
                exec_shell_cmd("cd %s/%s && mkdir build && cd build && cmake .. && make" % (WD+"/external", module))  
        else:
            exec_shell_cmd("cd %s/%s && ./configure && make" % (WD+"/external", module))

def create_static_libs():
    # libminiupnpc.a has already been created by 'create_external_libs'.
    modules = ['/contrib/epee/src','/src/blocks']
    for module in modules:
        if os.path.exists(WD+module+"/build"):
            exec_shell_cmd("cd %s && cd build && cmake .. && make" % (WD+module))
        else:
            exec_shell_cmd("cd %s && mkdir build && cd build && cmake .. && make" % (WD+module))

def create_shared_libs():    
    # In monerod, a total of 24 shared libraries are linked, 4 of which were previously installed as external libs.
    # And certain shared libs link 3 static libs, but they are pre-installed in the'creaste_external_libs' step.
    # In addition Monerod in not linked to "libdaemon_messagesd.so", but added because "libdaemon_rpc_serverd.so" linked by monerod links "libdaemon_messagesd.so".
    # Be careful with the build order of your modules, because there are links between modules.

    # modules = ['/src','/src/hardforks','/src/crypto','/src/common','/src/ringct/libringct_basicd.so','/src/checkpoints','/src/net','/src/rpc/librpc_based.so','/src/daemonizer','/src/device','/src/cryptonote_basic','/src/ringct/libringctd.so','/src/multisig','/src/blockchain_db','/src/cryptonote_core','/src/p2p','/src/cryptonote_protocol','/src/rpc/librpcd.so','/src/serializat','/src/rpc/libdaemon_messagesd.so','/src/rpc/libdaemon_rpc_serverd.so'] # Number of modules : 21 (24-4+1=21)
    
    if os.path.exists(WD+"/build"):
        exec_shell_cmd("cd %s && cd build && cmake .. && make" % (WD))
    else:
        exec_shell_cmd("cd %s && mkdir build && cd build && cmake .. && make" % (WD))        

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

@cmd_ex
class build_ext_ex(build_ext):
    pass

object1 = Extension('libOBJECT1',
          					include_dirs = LIST_CPP_INCLUDE_DIRS,
                    library_dirs = ['/usr/local/lib'],
                    define_macros = LIST_CPP_MACROS,
                    extra_compile_args = LIST_CC1_EXTRA_CLANG+LIST_CC1_EXTRA_OPT+LIST_CC1_EXTRA_DEBUG+LIST_CC1_EXTRA_WARNING+LIST_CC1_EXTRA_SPECIFIC_WARNING+LIST_AS_EXTRA_MACHINE,
                    #swig_opts=['-c++'],
                    sources = ['./src/daemon/command_parser_executor.cpp'])
object2 = Extension('libOBJECT2',
                    include_dirs = LIST_CPP_INCLUDE_DIRS,
                    library_dirs = ['/usr/local/lib'],
                    define_macros = LIST_CPP_MACROS,
                    extra_compile_args = LIST_CC1_EXTRA_CLANG+LIST_CC1_EXTRA_OPT+LIST_CC1_EXTRA_DEBUG+LIST_CC1_EXTRA_WARNING+LIST_CC1_EXTRA_SPECIFIC_WARNING+LIST_AS_EXTRA_MACHINE,
                    sources = ['./src/daemon/command_server.cpp'])
object3 = Extension('libOBJECT3',
                    include_dirs = LIST_CPP_INCLUDE_DIRS,
                    library_dirs = ['/usr/local/lib'],
                    define_macros = LIST_CPP_MACROS,
                    extra_compile_args = LIST_CC1_EXTRA_CLANG+LIST_CC1_EXTRA_OPT+LIST_CC1_EXTRA_DEBUG+LIST_CC1_EXTRA_WARNING+LIST_CC1_EXTRA_SPECIFIC_WARNING+LIST_AS_EXTRA_MACHINE,
                    sources = ['./src/daemon/daemon.cpp'])
object4 = Extension('libOBJECT4',
                    include_dirs = LIST_CPP_INCLUDE_DIRS,
                    library_dirs = ['/usr/local/lib'],
                    define_macros = LIST_CPP_MACROS,
                    extra_compile_args = LIST_CC1_EXTRA_CLANG+LIST_CC1_EXTRA_OPT+LIST_CC1_EXTRA_DEBUG+LIST_CC1_EXTRA_WARNING+LIST_CC1_EXTRA_SPECIFIC_WARNING+LIST_AS_EXTRA_MACHINE,
                    sources = ['./src/daemon/executor.cpp'])
object5 = Extension('libOBJECT5',
                    include_dirs = LIST_CPP_INCLUDE_DIRS,
                    library_dirs = ['/usr/local/lib'],
                    define_macros = LIST_CPP_MACROS,
                    extra_compile_args = LIST_CC1_EXTRA_CLANG+LIST_CC1_EXTRA_OPT+LIST_CC1_EXTRA_DEBUG+LIST_CC1_EXTRA_WARNING+LIST_CC1_EXTRA_SPECIFIC_WARNING+LIST_AS_EXTRA_MACHINE,
                    sources = ['./src/daemon/main.cpp'])
object6 = Extension('libOBJECT6',
                    include_dirs = LIST_CPP_INCLUDE_DIRS,
                    library_dirs = ['/usr/local/lib'],
                    define_macros = LIST_CPP_MACROS,
                    extra_compile_args = LIST_CC1_EXTRA_CLANG+LIST_CC1_EXTRA_OPT+LIST_CC1_EXTRA_DEBUG+LIST_CC1_EXTRA_WARNING+LIST_CC1_EXTRA_SPECIFIC_WARNING+LIST_AS_EXTRA_MACHINE,
                    sources = ['./src/daemon/rpc_command_executor.cpp'])

# setup (name = 'ObjectFiles',
#        version = '1.0',
#        description = 'Monero Damon Object Files',
#        author = 'Victork',
#        cmdclass = {'build_ext': build_ext_ex},
#        ext_modules = [object1,object2,object3,object4,object5,object6])


def create_objects(paths):
    print("--creating objects...")


if __name__ == '__main__':
    print ("-------------------------------------------------------------")
    print ("To compile monerod, the following file needs to be created.\n--1.Creating Object Files(6)\n--2.Creating Dependent Static libraries(4)\n--3.Creating Shared libraries(25)")
    print ("-------------------------------------------------------------")
    #exec_shell_cmd("git submodule update --init")

    #create_external_libs()
    #create_static_libs()
    create_shared_libs()






