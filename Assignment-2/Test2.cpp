//===- Software-Verification-Teaching Assignment 2-------------------------------------//
//
//     SVF: Static Value-Flow Analysis Framework for Source Code
//
// Copyright (C) <2013->
//

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//===-----------------------------------------------------------------------===//

/*
 // Software-Verification-Teaching Assignment 2 : ICFG graph traversal (Control-flow reachability analysis)
 //
 // 
 */


#include "Assignment-2.h"
#include "WPA/Andersen.h"

using namespace SVF;
using namespace SVFUtil;


int test1()
{
    std::vector<std::string> moduleNameVec = { "./Assignment-2/testcase/bc/test1.ll" };
    LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);
    LLVMModuleSet::getLLVMModuleSet()->dumpModulesToFile(".svf");

    SVFIRBuilder builder;
    SVFIR *svfir = builder.build();

    CallGraph* callgraph = AndersenWaveDiff::createAndersenWaveDiff(svfir)->getCallGraph();
    builder.updateCallGraph(callgraph);

    /// ICFG
    ICFG *icfg = svfir->getICFG();
    icfg->updateCallGraph(callgraph);
    icfg->dump("./Assignment-2/testcase/dot/test1.ll.icfg");

    ICFGTraversal *traversal = new ICFGTraversal(svfir, icfg);
    traversal->analyse();
    
    SVF::LLVMModuleSet::releaseLLVMModuleSet();
    SVF::SVFIR::releaseSVFIR();
    Set<std::string> expected = {"START: 0->1->3->4->END"};
    assert(expected == traversal->getPaths() && "test1 failed!");
    std::cout << SVFUtil::sucMsg("test1 passed!") << std::endl;
    delete traversal;
    return 0;
}



int test2()
{
    std::vector<std::string> moduleNameVec = { "./Assignment-2/testcase/bc/test2.ll"};

    LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);
    LLVMModuleSet::getLLVMModuleSet()->dumpModulesToFile(".svf");

    SVFIRBuilder builder;
    SVFIR *svfir = builder.build();

    CallGraph* callgraph = AndersenWaveDiff::createAndersenWaveDiff(svfir)->getCallGraph();
    builder.updateCallGraph(callgraph);

    /// ICFG
    ICFG *icfg = svfir->getICFG();
    icfg->updateCallGraph(callgraph);
    icfg->dump("./Assignment-2/testcase/dot/test2.ll.icfg");

    ICFGTraversal *traversal = new ICFGTraversal(svfir, icfg);
    traversal->analyse();
    Set<std::string> expected = {"START: 0->3->7->8->9->1->5->6->2->10->11->1->5->6->2->12->13->14->15->END"};
    assert(expected == traversal->getPaths() && "test2 failed!");
    std::cout << SVFUtil::sucMsg("test2 passed!") << std::endl;
    SVF::LLVMModuleSet::releaseLLVMModuleSet();
    SVF::SVFIR::releaseSVFIR();

    delete traversal;
    return 0;
}

int test3()
{
    
    std::vector<std::string> moduleNameVec = { "./Assignment-2/testcase/bc/test3.ll"};

    LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);
    LLVMModuleSet::getLLVMModuleSet()->dumpModulesToFile(".svf");

    SVFIRBuilder builder;
    SVFIR *svfir = builder.build();

    CallGraph* callgraph = AndersenWaveDiff::createAndersenWaveDiff(svfir)->getCallGraph();
    builder.updateCallGraph(callgraph);

    /// ICFG
    ICFG *icfg = svfir->getICFG();
    icfg->updateCallGraph(callgraph);
    icfg->dump("./Assignment-2/testcase/dot/test3.ll.icfg");

    ICFGTraversal *traversal = new ICFGTraversal(svfir, icfg);
    traversal->analyse();
    Set<std::string> expected = {"START: 0->3->19->1->5->6->8->10->12->END", "START: 0->3->19->1->5->6->7->9->11->14->END"};
    assert(expected == traversal->getPaths() && "test3 failed!");
    std::cout << SVFUtil::sucMsg("test3 passed!") << std::endl;
    SVF::LLVMModuleSet::releaseLLVMModuleSet();
    SVF::SVFIR::releaseSVFIR();

    delete traversal;
    return 0;
}

/*
 // Software-Verification-Teaching Assignment 2 main function entry
 // To run your testcase, please set the "program": "${workspaceFolder}/bin/assign-2" in file '.vscode/launch.json'
 // 
 */
int main(int argc, char **argv)
{
    int arg_num = 0;
    int extraArgc = 1;
    char **arg_value = new char *[argc + extraArgc];
    std::vector<std::string> moduleNameVec;
    for (; arg_num < argc; ++arg_num) {
        arg_value[arg_num] = argv[arg_num];
    }

    // add extra options
    int orgArgNum = arg_num;
    arg_value[arg_num++] = (char*) "-stat=false";
    assert(arg_num == (orgArgNum + extraArgc) && "more extra arguments? Change the value of extraArgc");
    
    moduleNameVec = OptionBase::parseOptions(
            arg_num, arg_value, "Software-Verification-Teaching Assignment 2", "[options]"
    );

    test1();
    test2();
    test3();
}
