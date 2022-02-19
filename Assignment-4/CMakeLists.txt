llvm_map_components_to_libnames(llvm_libs bitwriter core ipo irreader instcombine instrumentation target linker analysis scalaropts support )
include_directories(../include)

file (GLOB SOURCES
   ../Assignment-2/ICFGTraversal.cpp
   ../Assignment-3/Z3Mgr.cpp
   *.cpp
)
add_executable(assign-4 ${SOURCES})

target_link_libraries(assign-4 ${SVF_LIB} ${LLVMCudd} ${llvm_libs})
target_link_libraries(assign-4 ${Z3_LIBRARIES})

set_target_properties(assign-4 PROPERTIES
                       RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin )