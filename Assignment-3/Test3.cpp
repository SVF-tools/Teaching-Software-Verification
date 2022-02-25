//===- Software-Verification-Teaching Assignment 3-------------------------------------//
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
 // Software-Verification-Teaching Assignment 3 : Manual assertion-based verification (Z3 Example)
 //
 // 
 */

#include "Assignment-3.h"
#include "Util/Options.h"
using namespace z3;
using namespace SVF;
using namespace SVFUtil;


int main(int argc, char **argv) {
    Z3ExampleMgr* z3Mgr = new Z3ExampleMgr(1000);
    int points = 0;
    int n = (argc == 1) ? 0 : atoi(argv[1]);
    bool result;
    switch (n) {
        case 0:
            z3Mgr->test0(); // simple integers
            break;
        case 1:
            z3Mgr->test1(); // simple integers
            result = z3Mgr->EvalTrue(z3Mgr->getZ3Expr("b") == z3Mgr->getZ3Expr(1));
            break;
        case 2:
            z3Mgr->test2(); // one-level pointers
            result = z3Mgr->EvalTrue(z3Mgr->getZ3Expr("b") == z3Mgr->getZ3Expr(4));
            break;
        case 3:
            z3Mgr->test3(); // mutiple-level pointers
            result = z3Mgr->EvalTrue(z3Mgr->loadValue(z3Mgr->getZ3Expr("q")) == z3Mgr->getZ3Expr(10));
            break;
        case 4:
            z3Mgr->test4(); // array and pointers
            result = z3Mgr->EvalTrue(z3Mgr->getZ3Expr("a") == z3Mgr->getZ3Expr(10));
            break;

        case 5:
            z3Mgr->test5(); // struct and pointers
            result = z3Mgr->EvalTrue(z3Mgr->loadValue(z3Mgr->getZ3Expr("q")) == z3Mgr->getZ3Expr(10));
            break;
        
        case 6:
            z3Mgr->test6(); // branches
            result = z3Mgr->EvalTrue(z3Mgr->getZ3Expr("b") == z3Mgr->getZ3Expr(5));
            break;

        case 7:
            z3Mgr->test7(); // call
            result = z3Mgr->EvalTrue(z3Mgr->getZ3Expr("x") == z3Mgr->getZ3Expr(3));
            break;
        default:
            assert(false && "wrong test number! input from 0 to 7 only");
            break;
    }
    
    if (result == false) {
        // z3Mgr->printExprValues();
        std::cout << SVFUtil::errMsg("The test-") << SVFUtil::errMsg(std::to_string(n)) << SVFUtil::errMsg(" assertion is unsatisfiable!!") << std::endl;
        assert(false);
    }
    else {
        // z3Mgr->printExprValues();
        std::cout << SVFUtil::sucMsg("The test-") << SVFUtil::sucMsg(std::to_string(n)) << SVFUtil::sucMsg(" assertion is successfully verified!!") << std::endl;
    }
    return 0;
}