include_directories(../Z3Manager)
file (GLOB SOURCES
   ../Z3Manager/Z3Mgr.cpp
   *.cpp
)
add_executable(assign-3 ${SOURCES})

target_link_libraries(assign-3 ${SVF_LIB} ${llvm_libs})
target_link_libraries(assign-3 ${Z3_LIBRARIES})

set_target_properties(assign-3 PROPERTIES
                       RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin )