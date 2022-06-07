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

#ifndef SVF_ICFG_TRAVERSAL_H
#define SVF_ICFG_TRAVERSAL_H

#include "SVF-FE/SVFIRBuilder.h"

namespace SVF{

class ICFGTraversal
{
public:
    typedef std::vector<const Instruction*> CallStack;

    ICFGTraversal(SVFIR *s, ICFG *i) : svfir(s), icfg(i)
    {
    }

    /// Identify source node on ICFG
    std::set<const ICFGNode *> &identifySource(std::set<const ICFGNode *> &container)
    {
        container.insert(icfg->getGlobalICFGNode());
        return container;
    }

    /// Identify the sink node which is an assertion call on ICFG
    std::set<const ICFGNode *> &identifySink(std::set<const ICFGNode *> &container)
    {
        for (const CallICFGNode *cs : svfir->getCallSiteSet())
        {
            const SVFFunction *fun = SVFUtil::getCallee(cs->getCallSite());
            if (isAssertFun(fun))
                container.insert(cs);
        }
        return container;
    }

    /// Return true if this function is an assert function
    inline bool isAssertFun(const SVFFunction *fun) const{
        return (fun != NULL && (fun->getName() == "assert" || fun->getName() == "svf_assert" ||fun->getName() == "sink" ));
    }

    /// clear visited and callstack
    virtual void resetSolver(){
        visited.clear();
    }        

    /// Print the ICFG path
    virtual void printICFGPath();

    /// Depth-first-search ICFGTraversal on ICFG from src edge to dst node
    void dfs(const ICFGEdge *src, const ICFGNode *dst);

    void analyse();

    virtual bool handleCall(const CallCFGEdge* call) {  return true; }
    virtual bool handleRet(const RetCFGEdge* ret) {  return true; }
    virtual bool handleIntra(const IntraCFGEdge* edge) {  return true; }
    
    Set<std::string> getPaths(){
        return paths;
    }
private:
    ICFG *icfg;
    Set<std::string> paths;

protected:
    SVFIR *svfir;
    Set<std::pair<const ICFGEdge *, CallStack > > visited;
    CallStack callstack;
    std::vector<const ICFGEdge *> path;
};
}

#endif //SVF_EX_SSE_H
