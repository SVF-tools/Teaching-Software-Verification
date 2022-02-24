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
    std::vector<std::string> moduleNameVec = {"./Assignment-2/testcase/bc/test1.ll"};

    SVFModule *svfModule = LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);
    svfModule->buildSymbolTableInfo();
    LLVMModuleSet::getLLVMModuleSet()->dumpModulesToFile(".svf");

    SVFIRBuilder builder;
    SVFIR *svfir = builder.build(svfModule);

    PTACallGraph* callgraph = AndersenWaveDiff::createAndersenWaveDiff(svfir)->getPTACallGraph();
    builder.updateCallGraph(callgraph);

    /// ICFG
    ICFG *icfg = svfir->getICFG();
    icfg->updateCallGraph(callgraph);
    icfg->dump("./Assignment-2/testcase/dot/test1.ll.icfg");

    ICFGTraversal *traversal = new ICFGTraversal(svfir, icfg);
    traversal->analyse();
    
    SVF::LLVMModuleSet::releaseLLVMModuleSet();
    SVF::SVFIR::releaseSVFIR();
    Set<std::string> expected = {"START: 0->1->2->3->END"};
    assert(expected == traversal->getPaths() && "test1 failed!");
    std::cout << "test1 passed!" << "\n";
    delete traversal;
    return 0;
}



int test2()
{
    std::vector<std::string> moduleNameVec = {"./Assignment-2/testcase/bc/test2.ll"};

    SVFModule *svfModule = LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);
    svfModule->buildSymbolTableInfo();
    LLVMModuleSet::getLLVMModuleSet()->dumpModulesToFile(".svf");

    SVFIRBuilder builder;
    SVFIR *svfir = builder.build(svfModule);

    PTACallGraph* callgraph = AndersenWaveDiff::createAndersenWaveDiff(svfir)->getPTACallGraph();
    builder.updateCallGraph(callgraph);

    /// ICFG
    ICFG *icfg = svfir->getICFG();
    icfg->updateCallGraph(callgraph);
    icfg->dump("./Assignment-2/testcase/dot/test2.ll.icfg");

    ICFGTraversal *traversal = new ICFGTraversal(svfir, icfg);
    traversal->analyse();
    Set<std::string> expected = {"START: 0->5->6->7->8->1->2->3->4->9->10->11->12->END"};
    assert(expected == traversal->getPaths() && "test2 failed!");
    std::cout << "test2 passed!" << "\n";
    SVF::LLVMModuleSet::releaseLLVMModuleSet();
    SVF::SVFIR::releaseSVFIR();

    delete traversal;
    return 0;
}

int main(int argc, char **argv){
    test1();
    test2();
}