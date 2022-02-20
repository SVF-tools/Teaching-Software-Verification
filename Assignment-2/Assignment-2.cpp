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

using namespace SVF;
using namespace SVFUtil;

/// TODO: Implement your context-sensitive ICFG traversal here to traverse each program path (once for any loop) from src to dst
void ICFGTraversal::dfs(std::vector<const ICFGNode *> path, const ICFGNode *src, const ICFGNode *sink) {

}

/// TODO: print each path once this method is called, and
/// add each path as a string into std::set<std::string> paths
/// Print the path in the format "START: 1->2->4->5->END", where -> indicate an ICFGEdge connects two ICFGNode IDs
void ICFGTraversal::printICFGPath(std::vector<const ICFGNode *> &path)
{

}

/// TODO: Implement handle call
bool ICFGTraversal::handleCall(const CallCFGEdge* call){
    return true;
}

/// TODO: Implement handle ret
bool ICFGTraversal::handleRet(const RetCFGEdge* ret){
    return true;
}

bool ICFGTraversal::handleIntra(const IntraCFGEdge* edge){
    return true;
}

/// Program entry
void ICFGTraversal::analyse()
{
    std::set<const ICFGNode *> sources;
    std::set<const ICFGNode *> sinks;
    for (const ICFGNode *src : identifySource(sources)) {
        assert(SVFUtil::isa<GlobalICFGNode>(src) && "dfs should start with GlobalICFGNode!");
        for (const ICFGNode *sink: identifySink(sinks)) {
            handleIntra(new IntraCFGEdge(nullptr,const_cast<ICFGNode*>(src)));
            std::vector<const ICFGNode *> path;
            dfs(path, src, sink);
            resetSolver();
        }
    }
}