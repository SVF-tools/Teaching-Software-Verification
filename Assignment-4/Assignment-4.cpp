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

#include "Assignment-4.h"
#include "Util/Options.h"

using namespace SVF;
using namespace SVFUtil;
using namespace llvm;
using namespace z3;

static llvm::cl::opt<std::string> InputFilename(cl::Positional,
                                                llvm::cl::desc("<input bitcode>"), llvm::cl::init("-"));

/// TODO: Implement handling of function calls
bool SSE::handleCall(const CallCFGEdge* calledge){
    
    return true;
}

/// TODO: Implement handling of function returns
bool SSE::handleRet(const RetCFGEdge* retEdge){

    return true;
}

/// TODO: Implement handling of branch statement inside a function
bool SSE::handleBranch(const IntraCFGEdge* edge){
    return true;
}

/// TODO: Implement handling of non-branch statement inside a function
/// including handling of (1) AddrStmt, (2) CopyStmt, (3) LoadStmt, (4) StoreStmt and (5) GepStmt
bool SSE::handleNonBranch(const IntraCFGEdge* edge){

    const ICFGNode* dstNode = edge->getDstNode();
    const ICFGNode* srcNode = edge->getSrcNode();
    DBOP(if(!SVFUtil::isa<CallICFGNode>(dstNode) && !SVFUtil::isa<RetICFGNode>(dstNode)) std::cout << "\n## Analyzing "<< dstNode->toString() << "\n");

    for (const SVFStmt *stmt : dstNode->getSVFStmts())
    {
        if (const AddrStmt *addr = SVFUtil::dyn_cast<AddrStmt>(stmt))
        {
            /// TODO: Implement handling (1) AddrStmt
        }
        else if (const CopyStmt *copy = SVFUtil::dyn_cast<CopyStmt>(stmt))
        {
            /// TODO: Implement handling (2) CopyStmt
        }
        else if (const LoadStmt *load = SVFUtil::dyn_cast<LoadStmt>(stmt))
        {
            /// TODO: Implement handling (3) LoadStmt
        }
        else if (const StoreStmt *store = SVFUtil::dyn_cast<StoreStmt>(stmt))
        {
            /// TODO: Implement handling (4) StoreStmt
        }
        else if (const GepStmt *gep = SVFUtil::dyn_cast<GepStmt>(stmt))
        {
            /// TODO: Implement handling (5) GepStmt
        }
        else if (const BinaryOPStmt *binary = SVFUtil::dyn_cast<BinaryOPStmt>(stmt))
        {
            expr op0 = getZ3Expr(binary->getOpVarID(0));
            expr op1 = getZ3Expr(binary->getOpVarID(1));
            expr res = getZ3Expr(binary->getResID());
            switch (binary->getOpcode())
            {
            case BinaryOperator::Add:
                addToSolver(res == op0 + op1);
                break;
            case BinaryOperator::Sub:
                addToSolver(res == op0 - op1);
                break;
            case BinaryOperator::Mul:
                addToSolver(res == op0 * op1);
                break;
            case BinaryOperator::SDiv:
                addToSolver(res == op0 / op1);
                break;
            case BinaryOperator::SRem:
                addToSolver(res == op0 % op1);
                break;
            case BinaryOperator::Xor:
                addToSolver(int2bv(32, res) == (int2bv(32, op0) ^ int2bv(32, op1)));
                break;
            case BinaryOperator::And:
                addToSolver(int2bv(32, res) == (int2bv(32, op0) & int2bv(32, op1)));
                break;
            case BinaryOperator::Or:
                addToSolver(int2bv(32, res) == (int2bv(32, op0) | int2bv(32, op1)));
                break;
            case BinaryOperator::AShr:
                addToSolver(int2bv(32, res) == ashr(int2bv(32, op0), int2bv(32, op1)));
                break;
            case BinaryOperator::Shl:
                addToSolver(int2bv(32, res) == shl(int2bv(32, op0), int2bv(32, op1)));
                break;
            default:
                assert(false && "implement this part");
            }
        }
        else if (const CmpStmt *cmp = SVFUtil::dyn_cast<CmpStmt>(stmt))
        {
            expr op0 = getZ3Expr(cmp->getOpVarID(0));
            expr op1 = getZ3Expr(cmp->getOpVarID(1));
            expr res = getZ3Expr(cmp->getResID());
    
            auto predicate = cmp->getPredicate();
            switch (predicate)
            {
            case CmpInst::ICMP_EQ:
                addToSolver(res == ite(op0 == op1, getCtx().int_val(1), getCtx().int_val(0)));
                break;
            case CmpInst::ICMP_NE:
                addToSolver(res == ite(op0 != op1, getCtx().int_val(1), getCtx().int_val(0)));
                break;
            case CmpInst::ICMP_UGT:
            case CmpInst::ICMP_SGT:
                addToSolver(res == ite(op0 > op1, getCtx().int_val(1), getCtx().int_val(0)));
                break;
            case CmpInst::ICMP_UGE:
            case CmpInst::ICMP_SGE:
                addToSolver(res == ite(op0 >= op1, getCtx().int_val(1), getCtx().int_val(0)));
                break;
            case CmpInst::ICMP_ULT:
            case CmpInst::ICMP_SLT:
                addToSolver(res == ite(op0 < op1, getCtx().int_val(1), getCtx().int_val(0)));
                break;
            case CmpInst::ICMP_ULE:
            case CmpInst::ICMP_SLE:
                addToSolver(res == ite(op0 <= op1, getCtx().int_val(1), getCtx().int_val(0)));
                break;
            default:
                assert(false && "implement this part");
            }
        }
        else if (const UnaryOPStmt *unary = SVFUtil::dyn_cast<UnaryOPStmt>(stmt))
        {
            assert(false && "implement this part");
        }
        else if (const BranchStmt *br = SVFUtil::dyn_cast<BranchStmt>(stmt))
        {
            DBOP(std::cout << "\t skip handled when traversal Conditional IntraCFGEdge \n");
        }
        else if (const SelectStmt *select = SVFUtil::dyn_cast<SelectStmt>(stmt)) {
            expr res = getZ3Expr(select->getResID());
            expr tval = getZ3Expr(select->getTrueValue()->getId());
            expr fval = getZ3Expr(select->getFalseValue()->getId());
            expr cond = getZ3Expr(select->getCondition()->getId());
            addToSolver(res == ite(cond == getCtx().int_val(1), tval, fval));
        }
        else if (const PhiStmt *phi = SVFUtil::dyn_cast<PhiStmt>(stmt)) {
            expr res = getZ3Expr(phi->getResID());
            bool opINodeFound = false;
            for(u32_t i = 0; i < phi->getOpVarNum(); i++){
                assert(srcNode && "we don't have a predecessor ICFGNode?");
                if(phi->getOpICFGNode(i) == srcNode){
                    expr ope = getZ3Expr(phi->getOpVar(i)->getId());
                    addToSolver(res == ope);
                    opINodeFound = true;
                }
            }
            assert(opINodeFound && "predecessor ICFGNode of this PhiStmt not found?");
        }
        else if (const CallPE* callPE = SVFUtil::dyn_cast<CallPE>(stmt)){
        }
        else if (const RetPE* retPE = SVFUtil::dyn_cast<RetPE>(stmt)){
        }
        else
            assert(false && "implement this part");
    }

    return true;
}

/// TODO: Implement translatePath function
bool SSE::translatePath(std::vector<const ICFGEdge *> &path){

    return true;
}

bool SSE::assertchecking(const ICFGNode* inode){
    const CallICFGNode* callnode = SVFUtil::cast<CallICFGNode>(inode);
    assert(callnode && isAssertFun(getCallee(callnode->getCallSite()))  && "last node is not an assert call?");
    
    DBOP(std::cout << "\n## Analyzing "<< callnode->toString() << "\n");
    expr arg0 = getZ3Expr(callnode->getActualParms().at(0)->getId());
    addToSolver(arg0>0);
    if (getSolver().check() == unsat) {
        DBOP(printExprValues());
        assert(false && "The assertion is unsatisfiable");
        return false;
    }
    else {
        assert(getSolver().get_model().size() >=2 && "Model is empty?");
        DBOP(printExprValues());
        std::cout << SVFUtil::sucMsg("The assertion is successfully verified!!") << std::endl;
        return true;
    }
}

