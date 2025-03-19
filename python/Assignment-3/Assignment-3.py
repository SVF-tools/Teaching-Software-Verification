import z3
import sys
class Z3Mgr:
    def __init__(self, num_of_map_elems: int) -> None:
        self.ctx = z3.Context()
        self.solver = z3.Solver(ctx=self.ctx)
        self.var_id_to_expr_map = {}
        self.max_num_of_expr = num_of_map_elems
        self.str_to_id_map = {}
        self.current_expr_idx = 0

        self.addressMark = 0x7f000000

        index_sort = z3.IntSort(self.ctx)
        element_sort = z3.IntSort(self.ctx)
        array_sort = z3.ArraySort(index_sort, element_sort)
        self.loc_to_val_map = z3.Const('loc2ValMap', array_sort)

    def store_value(self, loc: z3.ExprRef, value: z3.ExprRef) -> z3.ExprRef:
        """
        Store a value at a memory location.

        Args:
            loc: Memory location expression
            value: Value expression to store

        Returns:
            Updated memory map expression
        """
        deref = self.get_eval_expr(loc)
        assert self.is_virtual_mem_address(deref.as_long()), "Pointer operand is not a physical address"
        self.loc_to_val_map = z3.Store(self.loc_to_val_map, deref, value)
        return self.loc_to_val_map


    def load_value(self, loc: z3.ExprRef) -> z3.ExprRef:
        """
        Load a value from a memory location.

        Args:
            loc: Memory location expression

        Returns:
            Value stored at the location
        """
        deref = self.get_eval_expr(loc)
        assert self.is_virtual_mem_address(deref.as_long()), "Pointer operand is not a physical address"
        return z3.Select(self.loc_to_val_map, deref)

    def get_eval_expr(self, e: z3.ExprRef) -> z3.ExprRef:
        if isinstance(e, int):
            e = z3.IntVal(e, self.ctx)
            return e
        else:
            res = self.solver.check()
            assert res != z3.unsat, "unsatisfied constraints! Check your contradictory constraints added to the solver"
            model = self.solver.model()
            return model.eval(e, model_completion=True)

    def has_z3_expr(self, expr_name: str) -> bool:
        return expr_name in self.str_to_id_map
    def get_z3_expr(self, expr_name: str) -> z3.ExprRef:
        if expr_name in self.str_to_id_map:
            return self.var_id_to_expr_map[self.str_to_id_map[expr_name]]
        else:
            self.current_expr_idx += 1
            self.str_to_id_map[expr_name] = self.current_expr_idx
            expr = z3.Int(str(expr_name), ctx=self.ctx)
            self.update_z3_expr(self.current_expr_idx, expr)
            return expr

    def update_z3_expr(self, idx: int, target: z3.ExprRef) -> None:
        if self.max_num_of_expr < idx + 1:
            raise IndexError("idx out of bound for map access, increase map size!")
        self.var_id_to_expr_map[idx] = target
    def get_z3_val(self, val:int) -> z3.ExprRef:
        return z3.IntVal(val, self.ctx)

    def is_virtual_mem_address(self, val: int) -> bool:
        return val > 0 and (val & self.addressMark) == self.addressMark
    def get_virtual_mem_address(self, idx: int) -> int:
        return self.addressMark + idx

    def get_memobj_address(self, expr_name: str) -> z3.ExprRef:
        self.get_z3_expr(expr_name)
        if expr_name in self.str_to_id_map:
            e = self.get_z3_val(self.get_virtual_mem_address(self.str_to_id_map[expr_name])).as_long()
            self.update_z3_expr(self.str_to_id_map[expr_name], e)
            return e
        else:
            assert False, "Invalid memory object name"

    def get_gepobj_address(self, base_expr: z3.ExprRef, offset: int) -> z3.ExprRef:
        base_obj_name = str(base_expr)
        if base_obj_name in self.str_to_id_map:
            base_obj_id = self.str_to_id_map[base_obj_name]
            gep_obj_id = base_obj_id + offset
            if base_obj_id == gep_obj_id:
                return base_expr
            else:
                gep_obj_id += self.max_num_of_expr/2
                e = self.get_z3_val(self.get_virtual_mem_address(gep_obj_id)).as_long()
                self.update_z3_expr(gep_obj_id, e)
                return e
        else:
            assert False, "Invalid base object name"


    def add_to_solver(self, expr: z3.ExprRef) -> None:
        self.solver.add(expr)

    def reset_solver(self) -> None:
        self.solver.reset()
        self.str_to_id_map = {}
        self.var_id_to_expr_map = {}
        self.current_expr_idx = 0
        self.loc_to_val_map = z3.Const('loc2ValMap', self.loc_to_val_map.sort())


    def print_expr_values(self):
        print("-----------Var and Value-----------")
        # for key,value
        for nIter, Id in self.str_to_id_map.items():
            e = self.get_eval_expr(self.get_z3_expr(nIter))
            # convert IntNumRef to int, or convert ArithRef to int
            value = e.as_long()
            exprName = f"Var{Id} ({nIter})"
            if self.is_virtual_mem_address(value):
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
        p = self.get_z3_expr("p")
    # int q;
        q = self.get_z3_expr("q")
    # int* r;
        r = self.get_z3_expr("r")
    # int x;
        x = self.get_z3_expr("x")
    # p = malloc();
        self.add_to_solver(p == self.get_memobj_address("p"))
    # q = 5;
        self.add_to_solver(q == 5)
    # *p = q;
        self.store_value(p, q)
    # x = *p;
        self.add_to_solver(x == self.load_value(p))
    # assert(x==5);
        self.add_to_solver(x == 5)

        res = self.solver.check()
        assert res == z3.sat, "Test 0 failed"
        print("Test 0 passed")

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



def check_negate_assert(z3_mgr, q):
    """
    Check the negation of the assertion.

    Args:
        z3_mgr: Instance of Z3Mgr
        q: Assertion to check

    Returns:
        True if the negation of the assertion is unsatisfiable, False otherwise
    """
    z3_mgr.solver.push()
    z3_mgr.add_to_solver(z3.Not(q))
    res = z3_mgr.solver.check() == z3.unsat
    z3_mgr.solver.pop()
    return res

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 Assignment-3.py test1")
        return 1

    z3_mgr = Z3Mgr(1000)
    result = False
    test_name = sys.argv[1]

    if test_name == "test0":
        z3_mgr.test0()
        q = z3_mgr.get_z3_expr("x") == z3_mgr.get_z3_val(5)
        res1 = check_negate_assert(z3_mgr, q)
        res2 = z3_mgr.has_z3_expr("x") and z3_mgr.get_eval_expr(z3_mgr.get_z3_expr("x")).as_long() == 5
        result = res1 and res2
    elif test_name == "test1":
        z3_mgr.test1()
        res2 = z3_mgr.has_z3_expr("b") and z3_mgr.get_eval_expr(z3_mgr.get_z3_expr("b")).as_long() == 1
        q = z3_mgr.get_z3_expr("b") > z3_mgr.get_z3_val(0)
        res1 = check_negate_assert(z3_mgr, q)
        result = res1 and res2
    elif test_name == "test2":
        z3_mgr.test2()
        res2 = z3_mgr.has_z3_expr("b") and z3_mgr.get_eval_expr(z3_mgr.get_z3_expr("b")).as_long() == 4
        q = z3_mgr.get_z3_expr("b") > z3_mgr.get_z3_val(3)
        res1 = check_negate_assert(z3_mgr, q)
        result = res1 and res2
    elif test_name == "test3":
        z3_mgr.test3()
        res2 = z3_mgr.has_z3_expr("q") and z3_mgr.get_eval_expr(z3_mgr.load_value(z3_mgr.get_z3_expr("q"))).as_long() == 10
        q = z3_mgr.get_z3_expr("x") == z3_mgr.get_z3_val(10)
        res1 = check_negate_assert(z3_mgr, q)
        result = res1 and res2
    elif test_name == "test4":
        z3_mgr.test4()
        res2 = z3_mgr.has_z3_expr("a") and z3_mgr.get_eval_expr(z3_mgr.get_z3_expr("a")).as_long() == 10
        q = z3_mgr.get_z3_expr("a") + z3_mgr.get_z3_expr("b") > z3_mgr.get_z3_val(20)
        res1 = check_negate_assert(z3_mgr, q)
        result = res1 and res2
    elif test_name == "test5":
        z3_mgr.test5()
        res2 = z3_mgr.has_z3_expr("b") and z3_mgr.get_eval_expr(z3_mgr.get_z3_expr("b")).as_long() == 5
        q = z3_mgr.get_z3_expr("b1") >= z3_mgr.get_z3_val(5)
        res1 = check_negate_assert(z3_mgr, q)
        result = res1 and res2
    elif test_name == "test6":
        z3_mgr.test6()
        res2 = z3_mgr.has_z3_expr("p") and z3_mgr.get_eval_expr(z3_mgr.load_value(z3_mgr.get_z3_expr("p"))).as_long() == 5
        q = z3_mgr.load_value(z3_mgr.get_z3_expr("p")) == z3_mgr.get_z3_val(5)
        res1 = check_negate_assert(z3_mgr, q)
        result = res1 and res2
    elif test_name == "test7":
        z3_mgr.test7()
        res2 = z3_mgr.has_z3_expr("d") and z3_mgr.get_eval_expr(z3_mgr.get_z3_expr("d")).as_long() == 5
        q = z3_mgr.get_z3_expr("d") == z3_mgr.get_z3_val(5)
        res1 = check_negate_assert(z3_mgr, q)
        result = res1 and res2
    elif test_name == "test8":
        z3_mgr.test8()
        res2 = z3_mgr.has_z3_expr("a") and z3_mgr.get_eval_expr(z3_mgr.get_z3_expr("a")).as_long() == 10 and \
               z3_mgr.has_z3_expr("p") and z3_mgr.get_eval_expr(
            z3_mgr.load_value(z3_mgr.get_z3_expr("p"))).as_long() == 0
        q = z3_mgr.load_value(z3_mgr.get_z3_expr("p")) == z3_mgr.get_z3_val(0)
        res1 = check_negate_assert(z3_mgr, q)
        result = res1 and res2
    elif test_name == "test9":
        z3_mgr.test9()
        res2 = z3_mgr.has_z3_expr("z") and z3_mgr.get_eval_expr(z3_mgr.get_z3_expr("z")).as_long() == 15
        q = z3_mgr.get_z3_expr("z") == z3_mgr.get_z3_val(15)
        res1 = check_negate_assert(z3_mgr, q)
        result = res1 and res2
    elif test_name == "test10":
        z3_mgr.test10()
        res2 = z3_mgr.has_z3_expr("x") and z3_mgr.get_eval_expr(z3_mgr.get_z3_expr("x")).as_long() == 3
        q = z3.And(z3_mgr.get_z3_expr("x") == z3_mgr.get_z3_val(3), z3_mgr.get_z3_expr("y") == z3_mgr.get_z3_val(2))
        res1 = check_negate_assert(z3_mgr, q)
        result = res1 and res2
    else:
        print("Invalid test name")
        return 1

    if result:
        print("test case passed!!")
    else:
        print(f"The test-{test_name} assertion is unsatisfiable!!")
        assert result

    z3_mgr.reset_solver()
    return 0

if __name__ == '__main__':
    main()






