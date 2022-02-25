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
            result = z3Mgr->test0().is_true(); // simple integers
            break;
        case 1:
            result = z3Mgr->test1().is_true(); // simple integers
            break;
        case 2:
            result = z3Mgr->test2().is_true(); // one-level pointers
            break;
        case 3:
            result = z3Mgr->test3().is_true(); // mutiple-level pointers
            break;
        case 4:
            result = z3Mgr->test4().is_true(); // array and pointers
            break;

        case 5:
            result = z3Mgr->test5().is_true() ; // struct and pointers
            break;
        
        case 6:
            result =z3Mgr->test6().is_true(); // branches
            break;

        case 7:
            result =z3Mgr->test7().is_true(); // call
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
    z3Mgr->resetSolver();
    delete z3Mgr;
    return 0;
}