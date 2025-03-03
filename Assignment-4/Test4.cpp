#include "Assignment-4.h"
#include "SVF-LLVM/LLVMUtil.h"
#include "Util/CommandLine.h"
#include "Util/Options.h"
#include "WPA/Andersen.h"

using namespace SVF;
using namespace SVFUtil;
u32_t SSE::assert_checked = 0;

/*
 // Software-Verification-Teaching Assignment 4 main function entry
 // To run your program with testcases , please set the bitcode from Assignment-2/Tests/testcases/sse/ for "args" in
 file'.vscode/launch.json'
 // e.g. To check test1, set "args": ["Assignment-2/Tests/testcases/sse/test1.ll"] in file'.vscode/launch.json'
 */
int main(int argc, char** argv) {
    int arg_num = 0;
    int extraArgc = 4;
    char** arg_value = new char*[argc + extraArgc];
    for (; arg_num < argc; ++arg_num) {
        arg_value[arg_num] = argv[arg_num];
    }
    std::vector<std::string> moduleNameVec;

    int orgArgNum = arg_num;
    arg_value[arg_num++] = (char*)"-model-arrays=true";
    arg_value[arg_num++] = (char*)"-pre-field-sensitive=false";
    arg_value[arg_num++] = (char*)"-model-consts=true";
    arg_value[arg_num++] = (char*)"-stat=false";
    assert(arg_num == (orgArgNum + extraArgc) && "more extra arguments? Change the value of extraArgc");

    moduleNameVec = OptionBase::parseOptions(arg_num,
                                             arg_value,
                                             "Software-Verification-Teaching Assignment 4",
                                             "[options] <input-bitcode...>");

    LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);
    LLVMModuleSet::getLLVMModuleSet()->dumpModulesToFile(".svf");

    SVFIRBuilder builder;
    SVFIR* svfir = builder.build();

    CallGraph* CallGraph = AndersenWaveDiff::createAndersenWaveDiff(svfir)->getCallGraph();
    builder.updateCallGraph(CallGraph);

    /// ICFG
    ICFG* icfg = svfir->getICFG();
    icfg->updateCallGraph(CallGraph);

    SSE* sse = new SSE(svfir, icfg);
    sse->analyse();

    SVF::LLVMModuleSet::releaseLLVMModuleSet();
    SVF::SVFIR::releaseSVFIR();

    delete[] arg_value;
    delete sse;
    if (SSE::assert_checked > 0) {
        return 0;
    }
    else {
        std::cerr << "No assertion was checked!" << std::endl;
        return 1;
    }
}