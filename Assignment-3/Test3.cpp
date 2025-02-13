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


// For assert (Q), add Q to solver
bool checkNegateAssert(Z3Examples* z3Mgr, z3::expr q) {

    // negative check
    z3Mgr->getSolver().push();
    z3Mgr->addToSolver(!q);
    z3Mgr->getSolver().check();
    bool res = z3Mgr->getSolver().check() == z3::unsat;
    z3Mgr->getSolver().pop();
    return res;
}

/*
 // Please set the "program": "${workspaceFolder}/bin/lab2" in file '.vscode/launch.json'
 // To run your testcase from 1-10, please set the string number for "args" in file'.vscode/launch.json'
 // e.g. To run test0, set "args": ["0"] in file'.vscode/launch.json'
 */
int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "Usage: ./lab2 test1" << std::endl;
        return 1;
    }
    Z3Examples* z3Mgr = new Z3Examples(1000);
    bool result;
    std::string test_name = argv[1];
    // Validate assert (i.e b>0) by proving non-existence of counterexamples,
    // Note that the validation code in `test1()` to `test2()` is not meant to be complete. Given a program prog and an assert `Q`,
    // you are expected to (1) translate the negation of `Q` and check unsat of `prog ∧ ¬Q` to prove the non-existence of counterexamples, and
    // (2) also evaluate individual variables’ values (e.g., `a`) if you know `a`’s value is 3. For example, z3Mgr->getEvalExpr(`a`) == 3.
    if (test_name == "test0") {
        z3Mgr->test0(); // simple integers
        //  assert(x==5);
        z3::expr q = (z3Mgr->getZ3Expr("x") == z3Mgr->getZ3Expr(5));
        bool res1 = checkNegateAssert(z3Mgr, q);
        bool res2 = z3Mgr->hasZ3Expr("x") && z3Mgr->z3Expr2NumValue(z3Mgr->getZ3Expr("x")) == 5;
        result = res1 && res2;
    }
    else if (test_name == "test1") {
        z3Mgr->test1(); // simple integers
        //  assert(b > 0);
        z3::expr q = (z3Mgr->getZ3Expr("b") > z3Mgr->getZ3Expr(0));
        bool res1 = checkNegateAssert(z3Mgr, q);
        bool res2 = z3Mgr->hasZ3Expr("b") && z3Mgr->z3Expr2NumValue(z3Mgr->getZ3Expr("b")) == 1;
        result = res1 && res2;
    }
    else if (test_name == "test2") {
        z3Mgr->test2(); // one-level pointers
        //   assert(b > 3);
        z3::expr q = (z3Mgr->getZ3Expr("b") > z3Mgr->getZ3Expr(3));
        bool res1 = checkNegateAssert(z3Mgr, q);
        bool res2 = z3Mgr->hasZ3Expr("b") && z3Mgr->z3Expr2NumValue(z3Mgr->getZ3Expr("b")) == 4;
        result = res1 && res2;
    }
    else if (test_name == "test3") {
        z3Mgr->test3(); // mutiple-level pointers
        // assert(x==10);
        z3::expr q = (z3Mgr->getZ3Expr("x") == z3Mgr->getZ3Expr(10));
        bool res1 = checkNegateAssert(z3Mgr, q);
        bool res2 = z3Mgr->hasZ3Expr("q") && z3Mgr->z3Expr2NumValue(z3Mgr->loadValue(z3Mgr->getZ3Expr("q"))) == 10;
        result = res1 && res2;
    }
    else if (test_name == "test4") {
        z3Mgr->test4(); // array and pointers
        // assert((a + b)>20);
        z3::expr q = (z3Mgr->getZ3Expr("a") + z3Mgr->getZ3Expr("b") > z3Mgr->getZ3Expr(20));
        bool res1 = checkNegateAssert(z3Mgr, q);
        bool res2 = z3Mgr->hasZ3Expr("a") && z3Mgr->z3Expr2NumValue(z3Mgr->getZ3Expr("a")) == 10;
        result = res1 && res2;
    }
    else if (test_name == "test5") {
        z3Mgr->test5(); // array and pointers
        // assert(b1 >= 5);
        z3::expr q = (z3Mgr->getZ3Expr("b1") >= z3Mgr->getZ3Expr(5));
        bool res1 = checkNegateAssert(z3Mgr, q);
        bool res2 = z3Mgr->hasZ3Expr("b") && z3Mgr->z3Expr2NumValue(z3Mgr->getZ3Expr("b")) == 5;
        result = res1 && res2;
    }
    else if (test_name == "test6") {
        z3Mgr->test6(); // array and pointers
        // assert(*p == 5);
        z3::expr q = (z3Mgr->loadValue(z3Mgr->getZ3Expr("p")) == z3Mgr->getZ3Expr(5));
        bool res1 = checkNegateAssert(z3Mgr, q);
        bool res2 = z3Mgr->hasZ3Expr("p") && z3Mgr->z3Expr2NumValue(z3Mgr->loadValue(z3Mgr->getZ3Expr("p"))) == 5;
        result = res1 && res2;
    }
    else if (test_name == "test7") {
        z3Mgr->test7(); // array and pointers
        // assert(d == 5);
        z3::expr q = (z3Mgr->getZ3Expr("d") == z3Mgr->getZ3Expr(5));
        bool res1 = checkNegateAssert(z3Mgr, q);
        bool res2 = z3Mgr->hasZ3Expr("d") && z3Mgr->z3Expr2NumValue(z3Mgr->getZ3Expr("d")) == 5;
        result = res1 && res2;
    }
    else if (test_name == "test8") {
        z3Mgr->test8(); // array and pointers
        // assert(*p == 0);
        z3::expr q = (z3Mgr->loadValue(z3Mgr->getZ3Expr("p")) == z3Mgr->getZ3Expr(0));
        bool res1 = checkNegateAssert(z3Mgr, q);
        bool res2 = z3Mgr->hasZ3Expr("a") && z3Mgr->z3Expr2NumValue(z3Mgr->getZ3Expr("a")) == 10
                    && z3Mgr->hasZ3Expr("p") && z3Mgr->z3Expr2NumValue(z3Mgr->loadValue(z3Mgr->getZ3Expr("p"))) == 0;
        result = res1 && res2;
    }
    else if (test_name == "test9") {
        z3Mgr->test9(); // branches
        //assert(z == 15);
        z3::expr q = (z3Mgr->getZ3Expr("z") == z3Mgr->getZ3Expr(15));
        bool res1 = checkNegateAssert(z3Mgr, q);
        bool res2 = z3Mgr->hasZ3Expr("z") && z3Mgr->z3Expr2NumValue(z3Mgr->getZ3Expr("z")) == 15;
        result = res1 && res2;
    }
    else if (test_name == "test10") {
        z3Mgr->test10(); // branches
        //  assert(x == 3 && y == 2);
        z3::expr q = (z3Mgr->getZ3Expr("x") == z3Mgr->getZ3Expr(3) && z3Mgr->getZ3Expr("y") == z3Mgr->getZ3Expr(2));
        bool res1 = checkNegateAssert(z3Mgr, q);
        bool res2 = z3Mgr->hasZ3Expr("x") && z3Mgr->z3Expr2NumValue(z3Mgr->getZ3Expr("x")) == 3;
        result = res1 && res2;
    }
    else {
        std::cerr << "Invalid test name" << std::endl;
        return 1;
    }

    if (result) {
        std::cout << "test case passed!!" << std::endl;
    }
    else {
        std::cout << SVFUtil::errMsg("The test-") << SVFUtil::errMsg(test_name)
                  << SVFUtil::errMsg(" assertion is unsatisfiable!!") << std::endl;
        assert(result);
    }
    z3Mgr->resetSolver();
    delete z3Mgr;
    return 0;
}