llvm_map_components_to_libnames(llvm_libs bitwriter core ipo irreader instcombine instrumentation target linker analysis scalaropts support )
include_directories(../Assignment-2)
include_directories(../Assignment-3)
file (GLOB SOURCES
   ../Assignment-2/ICFGTraversal.cpp
   ../Assignment-3/Z3Mgr.cpp
   *.cpp
)
add_executable(sse ${SOURCES})

target_link_libraries(sse ${SVF_LIB} ${LLVMCudd} ${llvm_libs})
target_link_libraries(sse ${Z3_LIBRARIES})

set_target_properties(sse PROPERTIES
                       RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin )