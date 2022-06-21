//===- CodeGraph.cpp -- -------------------------------------//
//
//                     SVF: Static Value-Flow Analysis
//
// Copyright (C) <2013->  <Yulei Sui>
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
 // SVFIR ICFG Generation
 //
 // Author: Guanqin Zhang  email: 152585@uts.edu.au
 */

#include "SVF-FE/LLVMUtil.h"
#include "Graphs/SVFG.h"
#include "WPA/Andersen.h"
#include "SABER/LeakChecker.h"
#include "SVF-FE/SVFIRBuilder.h"


using namespace SVF;
using namespace llvm;
using namespace std;

static llvm::cl::opt<std::string> InputFilename(cl::Positional,
        llvm::cl::desc("<input bitcode>"), llvm::cl::init("-"));

int main(int argc, char ** argv) {

    int arg_num = 0;
    int extraArgc = 4;
    char **arg_value = new char *[argc + extraArgc];
    std::vector<std::string> moduleNameVec;

    LLVMUtil::processArguments(argc, argv, arg_num, arg_value, moduleNameVec);
    // add extra options
    int orgArgNum = arg_num;
    arg_value[arg_num++] = (char*) "-model-consts=true";
    arg_value[arg_num++] = (char*) "-model-arrays=true";
    arg_value[arg_num++] = (char*) "-pre-field-sensitive=false";
    arg_value[arg_num++] = (char*) "-stat=false";
    assert(arg_num == (orgArgNum + extraArgc) && "more extra arguments? Change the value of extraArgc");

    llvm::cl::ParseCommandLineOptions(arg_num, arg_value,
                                "Whole Program Points-to Analysis\n");

    SVFModule* svfModule = LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);
    svfModule->buildSymbolTableInfo();

    /// Build Program Assignment Graph (SVFIR or PAG)
    SVFIRBuilder builder;
    SVFIR *svfir = builder.build(svfModule);
    // Dump pag
    svfir->dump(svfModule->getModuleIdentifier() + ".pag");
    /// ICFG
    ICFG *icfg = svfir->getICFG();
    // Dump icfg
    icfg->dump(svfModule->getModuleIdentifier() + ".icfg");

    // iterate each SVFVar on SVFIR
    std::map<NodeID, std::string> svfVarMap;
    for(SVFIR::iterator p = svfir->begin(); p != svfir->end();p++)
    {
        SVFVar *n = p->second;
        svfVarMap[p->first] =  n->toString();
    }

    for (auto it = svfVarMap.begin(); it != svfVarMap.end(); ++it) {
        std::cout  <<  it->second << "\n\n";
    }

    // iterate each ICFGNode on ICFG
    std::map<NodeID, std::string> icfgMap;
    for(ICFG::iterator i = icfg->begin(); i != icfg->end(); i++)
    {
        ICFGNode *n = i->second;
        icfgMap[i->first] =  n->toString();
    }

    for (auto it = icfgMap.begin(); it != icfgMap.end(); ++it) {
        std::cout  <<  it->second << "\n\n";
        // for(ICFGEdge* edge : icfg->getGNode(it->first)->getOutEdges()){
        //     SVFUtil::outs() << edge->toString() << "\n";
        // }
    }


    return 0;
}
