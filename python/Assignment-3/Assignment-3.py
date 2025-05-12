import z3
import sys
class Z3Mgr:
    def __init__(self, numOfMapElems: int) -> None:
        self.ctx = z3.Context()
        self.solver = z3.Solver(ctx=self.ctx)
        self.varIdToExprMap = {}
        self.maxNumOfExpr = numOfMapElems
        self.strToIdMap = {}
        self.currentExprIdx = 0

        self.addressMark = 0x7f000000

        indexSort = z3.IntSort(self.ctx)
        elementSort = z3.IntSort(self.ctx)
        arraySort = z3.ArraySort(indexSort, elementSort)
        self.locToValMap = z3.Const('loc2ValMap', arraySort)

    def storeValue(self, loc: z3.ExprRef, value: z3.ExprRef) -> z3.ExprRef:
        """
        Store a value at a memory location.

        Args:
            loc: Memory location expression
            value: Value expression to store

        Returns:
            Updated memory map expression
        """
        deref = self.getEvalExpr(loc)
        assert self.isVirtualMemAddress(deref.as_long()), "Pointer operand is not a physical address"
        self.locToValMap = z3.Store(self.locToValMap, deref, value)
        return self.locToValMap


    def loadValue(self, loc: z3.ExprRef) -> z3.ExprRef:
        """
        Load a value from a memory location.

        Args:
            loc: Memory location expression

        Returns:
            Value stored at the location
        """
        deref = self.getEvalExpr(loc)
        assert self.isVirtualMemAddress(deref.as_long()), "Pointer operand is not a physical address"
        return z3.Select(self.locToValMap, deref)

    def getEvalExpr(self, e: z3.ExprRef) -> z3.ExprRef:
        if isinstance(e, int):
            e = z3.IntVal(e, self.ctx)
            return e
        else:
            res = self.solver.check()
            assert res != z3.unsat, "unsatisfied constraints! Check your contradictory constraints added to the solver"
            model = self.solver.model()
            return model.eval(e, model_completion=True)

    def hasZ3Expr(self, exprName: str) -> bool:
        return exprName in self.strToIdMap
    def getZ3Expr(self, exprName: str) -> z3.ExprRef:
        if exprName in self.strToIdMap:
            return self.varIdToExprMap[self.strToIdMap[exprName]]
        else:
            self.currentExprIdx += 1
            self.strToIdMap[exprName] = self.currentExprIdx
            expr = z3.Int(str(exprName), ctx=self.ctx)
            self.updateZ3Expr(self.currentExprIdx, expr)
            return expr

    def updateZ3Expr(self, idx: int, target: z3.ExprRef) -> None:
        if self.maxNumOfExpr < idx + 1:
            raise IndexError("idx out of bound for map access, increase map size!")
        self.varIdToExprMap[idx] = target
    def getZ3Val(self, val:int) -> z3.ExprRef:
        return z3.IntVal(val, self.ctx)

    def isVirtualMemAddress(self, val: int) -> bool:
        return val > 0 and (val & self.addressMark) == self.addressMark
    def getVirtualMemAddress(self, idx: int) -> int:
        return self.addressMark + idx

    def getMemObjAddress(self, exprName: str) -> z3.ExprRef:
        self.getZ3Expr(exprName)
        if exprName in self.strToIdMap:
            e = self.getZ3Val(self.getVirtualMemAddress(self.strToIdMap[exprName])).as_long()
            self.updateZ3Expr(self.strToIdMap[exprName], e)
            return e
        else:
            assert False, "Invalid memory object name"

    def getGepObjAddress(self, baseExpr: z3.ExprRef, offset: int) -> z3.ExprRef:
        baseObjName = str(baseExpr)
        if baseObjName in self.strToIdMap:
            baseObjId = self.strToIdMap[baseObjName]
            gepObjId = baseObjId + offset
            if baseObjId == gepObjId:
                return baseExpr
            else:
                gepObjId += self.maxNumOfExpr/2
                e = self.getZ3Val(self.getVirtualMemAddress(gepObjId)).as_long()
                self.updateZ3Expr(gepObjId, e)
                return e
        else:
            assert False, "Invalid base object name"


    def addToSolver(self, expr: z3.ExprRef) -> None:
        self.solver.add(expr)

    def resetSolver(self) -> None:
        self.solver.reset()
        self.strToIdMap = {}
        self.varIdToExprMap = {}
        self.currentExprIdx = 0
        self.locToValMap = z3.Const('loc2ValMap', self.locToValMap.sort())


    def printExprValues(self):
        print("-----------Var and Value-----------")
        # for key,value
        for nIter, Id in self.strToIdMap.items():
            e = self.getEvalExpr(self.getZ3Expr(nIter))
            # convert IntNumRef to int, or convert ArithRef to int
            value = e.as_long()
            exprName = f"Var{Id} ({nIter})"
            if self.isVirtualMemAddress(value):
                print(f"{exprName}\t Value: {hex(value)}")
            else:
                print(f"{exprName}\t Value: {value}")
        print("-----------------------------------------")

    '''
    /* A simple example

    int main() {
        int* p;
        int q;
        int* r;
        int x;
    
        p = malloc();
        q = 5;
        *p = q;
        x = *p;
        assert(x==5);
    }
    */
    '''
    def test0(self):
    # int* p;
        p = self.getZ3Expr("p")
    # int q;
        q = self.getZ3Expr("q")
    # int* r;
        r = self.getZ3Expr("r")
    # int x;
        x = self.getZ3Expr("x")
    # p = malloc();
        self.addToSolver(p == self.getMemObjAddress("p"))
    # q = 5;
        self.addToSolver(q == 5)
    # *p = q;
        self.storeValue(p, q)
    # x = *p;
        self.addToSolver(x == self.loadValue(p))

    '''
    /*
    // Simple integers
    
        int main() {
            int a;
            int b;
            a = 0;
            b = a + 1;
            assert(b>0);
        }
    */
    '''
    def test1(self):
    # int a;
        
    # int b;
        
    # a = 0;
        
    # b = a + 1;
        pass



    '''
  // One-level pointers

    int main() {
		int* p;
		int q;
		int b;
		p = malloc;
		*p = 0;
		q = *p;
		*p = 3;
		b = *p + 1;
		assert(b > 3);
    }
    '''
    def test2(self):
    # int* p;
       
    # int q;
        
    # int b;
        
    # p = malloc;
       
    # *p = 0;
        
    # q = *p;
        
    # *p = 3;
       
    # b = *p + 1;
        pass


    '''
        // Mutiple-level pointers

    int main() {
        int** p;
        int* q;
        int* r;
        int x;

        p = malloc1(..);
        q = malloc2(..);
        *p = q;
        *q = 10;
        r = *p;
        x = *r;
        assert(x==10);
    }
    '''
    def test3(self):
    # int** p;
        
    # int* q;
       
    # int* r;
        
    # int x;
        
    # p = malloc1(..);
        
    # q = malloc2(..);
       
    # *p = q;
       
    # *q = 10;
        
    # r = *p;
        
    # x = *r;
        pass


    '''
       // Array and pointers

    int main() {
        int* p;
        int* x;
        int* y;
        int a;
        int b;
        p = malloc;
        x = &p[0];
        y = &p[1]
        *x = 10;
        *y = 11;
        a = *x;
        b = *y;
        assert((a + b)>20);
    }
    '''
    def test4(self):
    # int* p;
       
    # int* x;
        
    # int* y;
       
    # int a;
       
    # int b;
       
    # p = malloc;
       
    # x = &p[0];
        
    # y = &p[1];
        
    # *x = 10;
      
    # *y = 11;
   
    # a = *x;
    
    # b = *y;
        pass


    '''
    // Branches

int main(int argv) {
	int a;
	int b;
 	int b1;
	a = argv + 1;
	b = 5;
	if(a > 10)
 		b = a;
	b1 = b;
    assert(b1 >= 5);
}
    '''
    def test5(self):
    # int a;
        
    # int b;
        
    # int b1;
        
    # a = argv + 1;
        
    # b = 5;
        
    # if(a > 10)
    #     b = a;
    # b1 = b;
        pass


    '''
    int main() {
       int *a = malloc1;
       int *b = malloc2;
       *a = 5;
       *b = 10;
       int *p;
       if (*a < *b) {
           p = a;
       } else {
           p = b;
       }
       assert(*p == 5);
    }
    '''
    def test6(self):
    # int *a = malloc1;
        
    # int *b = malloc2;
        
    # *a = 5;
       
    # *b = 10;
     
    # int *p;
      
    # if (*a < *b) {
    #     p = a;
    # } else {
    #     p = b;
    # }
        pass


    '''
    // int main() {
    //	int a = 1, b = 2, c = 3;
    //	int d;
    //  if (a > 0) {
    //  	d = b + c;
    //  }
    //  else {
    //  	d = b - c;
    //  }
    //  assert(d == 5);
    // }
    '''
    def test7(self):
    # int a = 1, b = 2, c = 3;

    # int d;
        
    # if (a > 0) {
    # 	d = b + c;
    # }
    # else {
    # 	d = b - c;
    # }
        pass


    '''
    // int main() {
    //    int arr[2] = {0, 1};
    //    int a = 10;
    //	  int *p;
    //    if (a > 5) {
    //        p = &arr[0];
    //    }
    //    else {
    //        p = &arr[1];
    //    }
    //  assert(*p == 0);
    // }
    '''
    def test8(self):
        # int arr[2] = {0, 1};

        # int a = 10;
        
        # int *p;
        
        # if (a > 5) {
        #     p = &arr[0];
        # }
        # else {
        #     p = &arr[1];

        pass


    '''
        // Struct and pointers

    struct A{ int f0; int* f1;};
    int main() {
       struct A* p;
       int* x;
       int* q;
       int** r;
       int* y;
       int z;

       p = malloc1;
       x = malloc2;
       *x = 5;
       q = &(p->f0);
       *q = 10;
       r = &(p->f1);
       *r = x;
       y = *r;
       z = *q + *y;
       assert(z == 15);
    }
    '''
    def test9(self):
    # struct A{ int f0; int* f1;};
        
    # struct A* p;
        
    # int* x;
        
    # int* q;
        
    # int** r;
        
    # int* y;
        
    # int z;
       
    # p = malloc1;
        
    # x = malloc2;
        
    # *x = 5;
        
    # q = &(p->f0);
       
    # *q = 10;
        
    # r = &(p->f1);
      
    # *r = x;
      

    # y = *r;
       
    # z = *q + *y;
        pass


    '''
    int foo(int z) {
        k = z;
        return k;
    }
    int main() {
      int x;
      int y;
      y = foo(2);
      x = foo(3);
      assert(x == 3 && y == 2);
    }
    '''

    def test10(self):
    # int x;
        
    # int y;
        
    # y = foo(2);
        
    # int z, k
        
    # k = z;
        
    # return k;
        
    # x = foo(3);
       
    # int z, k
        
    # k = z;
        
    # return k;
        pass



def checkNegateAssert(z3Mgr, q):
    """
    Check the negation of the assertion.

    Args:
        z3Mgr: Instance of Z3Mgr
        q: Assertion to check

    Returns:
        True if the negation of the assertion is unsatisfiable, False otherwise
    """
    z3Mgr.solver.push()
    z3Mgr.addToSolver(z3.Not(q))
    res = z3Mgr.solver.check() == z3.unsat
    z3Mgr.solver.pop()
    return res

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 Assignment-3.py test1")
        return 1

    z3Mgr = Z3Mgr(1000)
    result = False
    testName = sys.argv[1]

    if testName == "test0":
        z3Mgr.test0()
        q = z3Mgr.getZ3Expr("x") == z3Mgr.getZ3Val(5)
        res1 = checkNegateAssert(z3Mgr, q)
        res2 = z3Mgr.hasZ3Expr("x") and z3Mgr.getEvalExpr(z3Mgr.getZ3Expr("x")).as_long() == 5
        result = res1 and res2
    elif testName == "test1":
        z3Mgr.test1()
        res2 = z3Mgr.hasZ3Expr("b") and z3Mgr.getEvalExpr(z3Mgr.getZ3Expr("b")).as_long() == 1
        q = z3Mgr.getZ3Expr("b") > z3Mgr.getZ3Val(0)
        res1 = checkNegateAssert(z3Mgr, q)
        result = res1 and res2
    elif testName == "test2":
        z3Mgr.test2()
        res2 = z3Mgr.hasZ3Expr("b") and z3Mgr.getEvalExpr(z3Mgr.getZ3Expr("b")).as_long() == 4
        q = z3Mgr.getZ3Expr("b") > z3Mgr.getZ3Val(3)
        res1 = checkNegateAssert(z3Mgr, q)
        result = res1 and res2
    elif testName == "test3":
        z3Mgr.test3()
        res2 = z3Mgr.hasZ3Expr("q") and z3Mgr.getEvalExpr(z3Mgr.loadValue(z3Mgr.getZ3Expr("q"))).as_long() == 10
        q = z3Mgr.getZ3Expr("x") == z3Mgr.getZ3Val(10)
        res1 = checkNegateAssert(z3Mgr, q)
        result = res1 and res2
    elif testName == "test4":
        z3Mgr.test4()
        res2 = z3Mgr.hasZ3Expr("a") and z3Mgr.getEvalExpr(z3Mgr.getZ3Expr("a")).as_long() == 10
        q = z3Mgr.getZ3Expr("a") + z3Mgr.getZ3Expr("b") > z3Mgr.getZ3Val(20)
        res1 = checkNegateAssert(z3Mgr, q)
        result = res1 and res2
    elif testName == "test5":
        z3Mgr.test5()
        res2 = z3Mgr.hasZ3Expr("b") and z3Mgr.getEvalExpr(z3Mgr.getZ3Expr("b")).as_long() == 5
        q = z3Mgr.getZ3Expr("b1") >= z3Mgr.getZ3Val(5)
        res1 = checkNegateAssert(z3Mgr, q)
        result = res1 and res2
    elif testName == "test6":
        z3Mgr.test6()
        res2 = z3Mgr.hasZ3Expr("p") and z3Mgr.getEvalExpr(z3Mgr.loadValue(z3Mgr.getZ3Expr("p"))).as_long() == 5
        q = z3Mgr.loadValue(z3Mgr.getZ3Expr("p")) == z3Mgr.getZ3Val(5)
        res1 = checkNegateAssert(z3Mgr, q)
        result = res1 and res2
    elif testName == "test7":
        z3Mgr.test7()
        res2 = z3Mgr.hasZ3Expr("d") and z3Mgr.getEvalExpr(z3Mgr.getZ3Expr("d")).as_long() == 5
        q = z3Mgr.getZ3Expr("d") == z3Mgr.getZ3Val(5)
        res1 = checkNegateAssert(z3Mgr, q)
        result = res1 and res2
    elif testName == "test8":
        z3Mgr.test8()
        res2 = z3Mgr.hasZ3Expr("a") and z3Mgr.getEvalExpr(z3Mgr.getZ3Expr("a")).as_long() == 10 and \
               z3Mgr.hasZ3Expr("p") and z3Mgr.getEvalExpr(
            z3Mgr.loadValue(z3Mgr.getZ3Expr("p"))).as_long() == 0
        q = z3Mgr.loadValue(z3Mgr.getZ3Expr("p")) == z3Mgr.getZ3Val(0)
        res1 = checkNegateAssert(z3Mgr, q)
        result = res1 and res2
    elif testName == "test9":
        z3Mgr.test9()
        res2 = z3Mgr.hasZ3Expr("z") and z3Mgr.getEvalExpr(z3Mgr.getZ3Expr("z")).as_long() == 15
        q = z3Mgr.getZ3Expr("z") == z3Mgr.getZ3Val(15)
        res1 = checkNegateAssert(z3Mgr, q)
        result = res1 and res2
    elif testName == "test10":
        z3Mgr.test10()
        res2 = z3Mgr.hasZ3Expr("x") and z3Mgr.getEvalExpr(z3Mgr.getZ3Expr("x")).as_long() == 3
        q = z3.And(z3Mgr.getZ3Expr("x") == z3Mgr.getZ3Val(3), z3Mgr.getZ3Expr("y") == z3Mgr.getZ3Val(2))
        res1 = checkNegateAssert(z3Mgr, q)
        result = res1 and res2
    else:
        print("Invalid test name")
        return 1

    if result:
        print("test case passed!!")
    else:
        print(f"The test-{testName} assertion is unsatisfiable!!")
        assert result

    z3Mgr.resetSolver()
    return 0

if __name__ == '__main__':
    main()






