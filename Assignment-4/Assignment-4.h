//===- Software-Verification-Teaching Assignment 4-------------------------------------//
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
 // Software-Verification-Teaching Assignment 4 : Automated assertion-based verification (Static symbolic execution)
 //
 // 
 */

#ifndef SVF_EX_SSE_H
#define SVF_EX_SSE_H

#include "Assignment-2.h"
#include "Z3Mgr.h"
#include <stdlib.h>
namespace SVF{

class SSE : public ICFGTraversal
{

public:
    /// Constructor
    SSE(SVFIR *s, ICFG *i): ICFGTraversal(s,i)
    {
        z3Mgr = new Z3SSEMgr(s);
    }
    /// Destructor
    virtual ~SSE(){
        delete z3Mgr;
    }

    inline z3::solver& getSolver() {
        return z3Mgr->getSolver();
    }

    inline z3::context& getCtx() {
        return z3Mgr->getCtx();
    }

    /// Add expr to Z3 solver
    void addToSolver(z3::expr e){
        DBOP(std::cout << "==> " << e.simplify() << "\n");
        getSolver().add(e);
    }

    /// Return Z3 expression based on ValVar ID
    inline z3::expr getZ3Expr(NodeID idx) const{
        return z3Mgr->getZ3Expr(idx);
    }
    
    /// Return Z3 expression based on ObjVar ID
    inline z3::expr getMemObjAddress(NodeID idx) const{
        return z3Mgr->getMemObjAddress(idx);
    }
    /// Return int value from an expression if it is a numeral, otherwise return an approximate value
    inline z3::expr getEvalExpr(z3::expr e) {
        return z3Mgr->getEvalExpr(e);
    }

    /// Dump values of all exprs
    inline void printExprValues(){
        z3Mgr->printExprValues();
    }

    /// Print the ICFG path
    void printICFGPath(){
        ICFGTraversal::printICFGPath();
        if(translatePath(path))
            assertchecking(path.back()->getDstNode());
        resetSolver();
    }

    /// clear visited, callstack and solver
    void resetSolver(){
        getSolver().reset();
    }        

    /// Encode the path into Z3 constraints and return true if the path is feasible, false otherwise.
    bool translatePath(std::vector<const ICFGEdge *> &path);

    /// Return true if svf_assert check is successful
    bool assertchecking(const ICFGNode* edge);

    bool handleCall(const CallCFGEdge* call);
    bool handleRet(const RetCFGEdge* ret);
    bool handleIntra(const IntraCFGEdge* edge){
        if(edge->getCondition()) {
            if (handleBranch(edge) == false)
                return false;
            else {
                // if edge is from "br if.end" to stmt after if.end, should handle it as non branch
                return handleNonBranch(edge);
            }
        }
        else {
            return handleNonBranch(edge);
        }
    }
    bool handleNonBranch(const IntraCFGEdge* edge);
    bool handleBranch(const IntraCFGEdge* edge);

private:
    Z3SSEMgr* z3Mgr;
};

}

#endif //SVF_EX_SSE_H
