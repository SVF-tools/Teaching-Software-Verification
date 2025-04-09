import z3
import pysvf
import sys
class Z3Mgr:
    def __init__(self, svfir: pysvf.SVFIR) -> None:
        self.pag = svfir

        self.ctx = z3.Context()
        self.solver = z3.Solver(ctx=self.ctx)
        self.var_id_to_expr_map = {}
        self.max_num_of_expr = svfir.get_pag_node_num()*10
        self.current_expr_idx = 0

        self.addressMask = 0x7f000000
        self.flippedAddressMask = (self.addressMask^0xffffffff)

        index_sort = z3.IntSort(self.ctx)
        element_sort = z3.IntSort(self.ctx)
        array_sort = z3.ArraySort(index_sort, element_sort)
        self.loc_to_val_map = z3.Const('loc2ValMap', array_sort)

    def get_internal_id(self, addr: int) -> int:
        return addr & self.flippedAddressMask

    def create_expr_for_obj_var(self, obj_var: pysvf.ObjVar) -> z3.ExprRef:
        base_obj_var = self.pag.get_base_object(obj_var.get_id())
        if base_obj_var.is_const_data_or_agg_data() or base_obj_var.is_constant_array() or base_obj_var.is_constant_struct():
            if base_obj_var.is_const_int_obj_var():
                obj = base_obj_var.as_const_int_obj_var()
                return z3.IntVal(obj.get_sext_value(), self.ctx)
            elif base_obj_var.as_const_data().is_const_fp_obj_var():
                obj = base_obj_var.as_const_data().as_const_fp_obj_var()
                return z3.IntVal(obj.get_fp_value(), self.ctx)
            elif base_obj_var.is_global_obj_var():
                return z3.IntVal(self.get_virtual_mem_address(obj_var.get_id()), self.ctx)
            elif base_obj_var.is_constant_array() or base_obj_var.is_constant_struct():
                assert False, "implement this part"
            else:
                assert False, "what other types of values we have?"
        else:
            return z3.IntVal(self.get_virtual_mem_address(obj_var.get_id()), self.ctx)


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
        res = self.solver.check()
        assert res != z3.unsat, "unsatisfied constraints! Check your contradictory constraints added to the solver"
        model = self.solver.model()
        return model.eval(e)


    def get_z3_expr(self, idx: int, calling_ctx: list) -> z3.ExprRef:
        assert self.get_internal_id(idx) == idx, "idx cannot be addressValue > 0x7f000000."
        svf_var = self.pag.get_gnode(idx)
        if svf_var.is_obj_var():
            return self.create_expr_for_obj_var(svf_var.as_obj_var())
        else:
            if not isinstance(svf_var, pysvf.ConstIntValVar) and not isinstance(svf_var, pysvf.ConstIntObjVar):
                pass
            else:
                pass
            name = "ValVar" + str(idx)
            return z3.Int(name, self.ctx)


    def calling_ctx_to_str(self, calling_ctx: list) -> str:
        rawstr = ""
        rawstr += "ctx:[ "
        for node in calling_ctx:
            rawstr += str(node.get_id()) + " "
        rawstr += "] "
        return rawstr


    def update_z3_expr(self, idx: int, target: z3.ExprRef) -> None:
        if self.max_num_of_expr < idx + 1:
            raise IndexError("idx out of bound for map access, increase map size!")
        self.var_id_to_expr_map[idx] = target

    def get_z3_val(self, val:int) -> z3.ExprRef:
        return z3.IntVal(val, self.ctx)

    def is_virtual_mem_address(self, val: int) -> bool:
        return val > 0 and (val & self.addressMask) == self.addressMask

    def get_virtual_mem_address(self, idx: int) -> int:
        return self.addressMask + idx

    def get_memobj_address(self, addr: int) -> z3.ExprRef:
        #print(addr)
        obj_idx = self.get_internal_id(addr)
        assert(self.pag.get_gnode(obj_idx).is_obj_var()), "Invalid memory object index"
        return self.create_expr_for_obj_var(self.pag.get_gnode(obj_idx).as_obj_var())

    def z3_expr_to_num_value(self, expr: z3.ExprRef) -> int:
        val = z3.simplify(self.get_eval_expr(expr))
        if isinstance(val, z3.IntNumRef):
            return val.as_long()
        elif val.is_numeral():
            return val.as_long()
        else:
            assert False, "this expression is not numeral"
            sys.exit(1)

    def get_gepobj_address(self, base_expr: z3.ExprRef, offset: int) -> z3.ExprRef:

        obj = self.get_internal_id(self.z3_expr_to_num_value(base_expr))
        assert(self.pag.get_gnode(obj).is_obj_var()), "Fail to get the base object address!"
        gep_obj = self.pag.get_gep_obj_var(obj, offset)
        if obj == gep_obj:
            return self.create_expr_for_obj_var(self.pag.get_gnode(obj).as_obj_var())
        else:
            return self.create_expr_for_obj_var(self.pag.get_gnode(gep_obj).as_gep_obj_var())


    def get_gep_offset(self, gep: pysvf.GepStmt, callingCtx: list) -> int:
        if len(gep.get_offset_var_and_gep_type_pair_vec()) == 0:
            return gep.get_constant_struct_fld_idx()
        total_offset = 0
        for i in range(len(gep.get_offset_var_and_gep_type_pair_vec()) - 1, -1, -1):
            var = gep.get_offset_var_and_gep_type_pair_vec()[i][0]
            type = gep.get_offset_var_and_gep_type_pair_vec()[i][1]
            offset = 0
            if var.is_const_int_val_var():
                offset = var.as_const_int_val_var().get_sext_value()
            else:
                offset = self.get_eval_expr(self.get_z3_expr(var.get_id(), callingCtx)).as_long()
            if type is None:
                total_offset += offset
                continue
            if type.is_pointer_type():
                total_offset += offset * self.pag.get_num_of_flatten_elements(gep.get_src_pointee_type())
            else:
                total_offset += self.pag.get_flattened_elem_idx(type, offset)
        return total_offset

    def print_expr_values(self, callingCtx:list):
        print_val_map = {}
        obj_key_map = {}
        val_key_map = {}
        for nIter in range(self.pag.get_pag_node_num()):
            idx = nIter
            node = self.pag.get_gnode(idx)
            e = self.get_eval_expr(self.get_z3_expr(idx, callingCtx))
            if z3.is_int_value(e) == False:
                continue
            if isinstance(node, pysvf.ValVar):
                if self.is_virtual_mem_address(e.as_long()):
                    valstr = "\t Value: " + hex(e.as_long()) + "\n"
                else:
                    valstr = "\t Value: " + str(e.as_long()) + "\n"
                print_val_map["ValVar" + str(idx)] = valstr
                val_key_map[idx] = "ValVar" + str(idx)
            else:
                if self.is_virtual_mem_address(e.as_long()):
                    stored_value = self.get_eval_expr(self.load_value(e))
                    if z3.is_int_value(stored_value) == False:
                        continue
                    if isinstance(stored_value, z3.ExprRef):
                        if self.is_virtual_mem_address(stored_value.as_long()):
                            valstr = "\t Value: " + hex(stored_value.as_long()) + "\n"
                        else:
                            valstr = "\t Value: " + str(stored_value.as_long()) + "\n"
                    else:
                        valstr = "\t Value: NULL" + "\n"
                else:
                    valstr = "\t Value: NULL" + "\n"
                print_val_map["ObjVar" + str(idx) + " (0x" + hex(idx) + ") "] = valstr
                obj_key_map[idx] = "ObjVar" + str(idx) + " (0x" + hex(idx) + ") "
        print("\n-----------SVFVar and Value-----------")
        for idx, key in obj_key_map.items():
            val = print_val_map[key].strip()
            label = f"ObjVar{idx} (0x{idx:x})"
            print(f"{label:<30} {val}")

        for idx, key in val_key_map.items():
            val = print_val_map[key].strip()
            label = f"ValVar{idx}"
            print(f"{label:<30} {val}")
        print("-----------------------------------------")

    def add_to_solver(self, expr: z3.ExprRef) -> None:
        self.solver.add(expr)

    def reset_solver(self) -> None:
        self.solver.reset()
        self.var_id_to_expr_map = {}
        self.current_expr_idx = 0
        self.loc_to_val_map = z3.Const('loc2ValMap', self.loc_to_val_map.sort())


class Assignment4:
    def __init__(self, svfir: pysvf.SVFIR) -> None:
        self.svfir = svfir
        self.icfg = self.svfir.get_icfg()
        self.z3mgr = Z3Mgr(svfir)
        self.calling_ctx = []
        self.paths = []

        self.path = []
        self.visited = set()

    def get_z3mgr(self) -> Z3Mgr:
        return self.z3mgr

    def identify_source(self) -> list:
        return [self.icfg.get_global_icfg_node()]

    def identify_sink(self) -> list:
        res = []
        cs = self.svfir.get_call_sites()
        for c in cs:
            func_name = c.get_called_function().get_name()
            if func_name == "assert" or func_name == "svf_assert" or func_name == "sink":
                res.append(c)
        return res

    def is_assert_func(self, func_name: str) -> bool:
        return func_name == "assert" or func_name == "svf_assert" or func_name == "sink"

    def reset_solver(self) -> None:
        self.z3mgr.reset_solver()
        self.calling_ctx = []



    def translate_path(self, path: list) -> bool:
        for edge in path:
            if edge.is_intra_cfg_edge():
                if not self.handle_intra(edge):
                    return False
            elif edge.is_call_cfg_edge():
                self.handle_call(edge)
            elif edge.is_ret_cfg_edge():
                self.handle_ret(edge)
            else:
                assert False, "what other edges we have?"
        return True


    def assert_checking(self, inode: pysvf.ICFGNode) -> bool:
        assert_checked = 0
        callnode = inode
        assert callnode and self.is_assert_func(callnode.get_called_function().get_name()) and "last node is not an assert call?"
        print(f"## Analyzing {callnode}")
        arg0 = self.z3mgr.get_z3_expr(callnode.get_actual_parms()[0].get_id(), self.calling_ctx)
        self.z3mgr.solver.push()
        self.z3mgr.add_to_solver(arg0 == self.z3mgr.get_z3_val(0))

        if self.z3mgr.solver.check() != z3.unsat:
            self.z3mgr.solver.pop()
            self.z3mgr.print_expr_values(self.calling_ctx)
            ss = f"The assertion is unsatisfiable!! ({inode})"
            ss += f"Counterexample: {self.z3mgr.solver.model()}"
            print(ss)
            print(self.z3mgr.solver)
            assert False
        else:
            self.z3mgr.solver.pop()
            self.z3mgr.print_expr_values(self.calling_ctx)
            print(self.z3mgr.solver)
            ss = f"The assertion is successfully verified!! ({inode})"
            print(ss)
            return True

    def push_calling_ctx(self, c: pysvf.ICFGNode) -> None:
        self.calling_ctx.append(c)

    def pop_calling_ctx(self) -> None:
        self.calling_ctx.pop()

    def analyse(self) -> None:
        for src in self.identify_source():
            assert isinstance(src, pysvf.GlobalICFGNode) and "reachability should start with GlobalICFGNode!"
            for sink in self.identify_sink():
                self.reachability(pysvf.IntraCFGEdge(None, src), sink)
                self.reset_solver()

    def handle_branch(self, edge: pysvf.IntraCFGEdge) -> bool:
        assert edge.get_condition() and "not a conditional control-flow transfer?"
        cond = self.z3mgr.get_z3_expr(edge.get_condition().get_id(), self.calling_ctx)
        successor_val = self.z3mgr.get_z3_val(edge.get_successor_cond_value())
        self.z3mgr.solver.push()
        self.z3mgr.add_to_solver(cond == successor_val)
        res = self.z3mgr.solver.check()
        self.z3mgr.solver.pop()
        if res == z3.unsat:
            print("This conditional ICFGEdge is infeasible!!")
            return False
        else:
            print("This conditional ICFGEdge is feasible")
            self.z3mgr.add_to_solver(cond == successor_val)
            return True


    # TODO: Implement handling of function calls
    def handle_call(self, edge: pysvf.CallCFGEdge) -> None:
        pass


    # TODO: Implement handling of function returns
    def handle_ret(self, edge: pysvf.RetCFGEdge) -> None:
        pass

    def handle_intra(self, edge: pysvf.IntraCFGEdge) -> bool:
        if edge.get_condition():
            if self.handle_branch(edge) is False:
                return False

        dst_node = edge.get_dst()
        src_node = edge.get_src()
        for stmt in dst_node.get_svf_stmts():
            if isinstance(stmt, pysvf.AddrStmt):
                # TODO: Implement handling (1) AddrStmt
                pass
            elif isinstance(stmt, pysvf.CopyStmt):
                # TODO: Implement handling (2) CopyStmt
                pass
            elif isinstance(stmt, pysvf.LoadStmt):
                # TODO: Implement handling (3) LoadStmt
                pass
            elif isinstance(stmt, pysvf.StoreStmt):
                # TODO: Implement handling (4) StoreStmt
                pass
            elif isinstance(stmt, pysvf.GepStmt):
                # TODO: Implement handling (5) GepStmt
                pass
            elif isinstance(stmt, pysvf.CmpStmt):
                stmt = stmt.as_cmp_stmt()
                op0 = self.z3mgr.get_z3_expr(stmt.get_op_var(0).get_id(), self.calling_ctx)
                op1 = self.z3mgr.get_z3_expr(stmt.get_op_var(1).get_id(), self.calling_ctx)
                res = self.z3mgr.get_z3_expr(stmt.get_res_id(), self.calling_ctx)
                predicate = stmt.get_predicate()
                if predicate == pysvf.Predicate.ICMP_EQ:
                    self.z3mgr.add_to_solver(res == z3.If(op0 == op1, 1, 0))
                elif predicate == pysvf.Predicate.ICMP_NE:
                    self.z3mgr.add_to_solver(res == z3.If(op0 != op1, 1, 0))
                elif predicate == pysvf.Predicate.ICMP_UGT or predicate == pysvf.Predicate.ICMP_SGT:
                    self.z3mgr.add_to_solver(res == z3.If(op0 > op1, 1, 0))
                elif predicate == pysvf.Predicate.ICMP_UGE or predicate == pysvf.Predicate.ICMP_SGE:
                    self.z3mgr.add_to_solver(res == z3.If(op0 >= op1, 1, 0))
                elif predicate == pysvf.Predicate.ICMP_ULT or predicate == pysvf.Predicate.ICMP_SLT:
                    self.z3mgr.add_to_solver(res == z3.If(op0 < op1, 1, 0))
                elif predicate == pysvf.Predicate.ICMP_ULE or predicate == pysvf.Predicate.ICMP_SLE:
                    self.z3mgr.add_to_solver(res == z3.If(op0 <= op1, 1, 0))
                else:
                    assert False, "implement this part"
            elif isinstance(stmt, pysvf.BinaryOPStmt):
                stmt = stmt.as_binary_op_stmt()
                op0 = self.z3mgr.get_z3_expr(stmt.get_op_var(0).get_id(), self.calling_ctx)
                op1 = self.z3mgr.get_z3_expr(stmt.get_op_var(1).get_id(), self.calling_ctx)
                res = self.z3mgr.get_z3_expr(stmt.get_res_id(), self.calling_ctx)
                opcode = stmt.get_op()
                if opcode == pysvf.OpCode.Add:
                    self.z3mgr.add_to_solver(res == op0 + op1)
                elif opcode == pysvf.OpCode.Sub:
                    self.z3mgr.add_to_solver(res == op0 - op1)
                elif opcode == pysvf.OpCode.Mul:
                    self.z3mgr.add_to_solver(res == op0 * op1)
                elif opcode == pysvf.OpCode.SDiv:
                    self.z3mgr.add_to_solver(res == op0 / op1)
                elif opcode == pysvf.OpCode.SRem:
                    self.z3mgr.add_to_solver(res == op0 % op1)
                elif opcode == pysvf.OpCode.Xor:
                    self.z3mgr.add_to_solver(res == z3.bv2int(z3.int2bv(32, op0) ^ z3.int2bv(32, op1), 1))
                elif opcode == pysvf.OpCode.And:
                    self.z3mgr.add_to_solver(res == z3.bv2int(z3.int2bv(32, op0) & z3.int2bv(32, op1), 1))
                elif opcode == pysvf.OpCode.Or:
                    self.z3mgr.add_to_solver(res == z3.bv2int(z3.int2bv(32, op0) | z3.int2bv(32, op1), 1))
                elif opcode == pysvf.OpCode.AShr:
                    self.z3mgr.add_to_solver(res == z3.bv2int(z3.ashr(z3.int2bv(32, op0), z3.int2bv(32, op1)), 1))
                elif opcode == pysvf.OpCode.Shl:
                    self.z3mgr.add_to_solver(res == z3.bv2int(z3.shl(z3.int2bv(32, op0), z3.int2bv(32, op1)), 1))
                else:
                    assert False, "implement this part"
            elif isinstance(stmt, pysvf.BranchStmt):
                pass

            elif isinstance(stmt, pysvf.PhiStmt):
                stmt = stmt.as_phi_stmt()
                res = self.z3mgr.get_z3_expr(stmt.get_res_id(), self.calling_ctx)
                opINodeFound = False
                for i in range(stmt.get_op_var_num()):
                    assert src_node and "we don't have a predecessor ICFGNode?"
                    if src_node.get_fun().post_dominates(src_node.get_bb(), stmt.get_op_icfg_node(i).get_bb()):
                        ope = self.z3mgr.get_z3_expr(stmt.get_op_var(i).get_id(), self.calling_ctx)
                        self.z3mgr.add_to_solver(res == ope)
                        opINodeFound = True
                assert opINodeFound and "predecessor ICFGNode of this PhiStmt not found?"

        return True


    '''
    /// TODO: Implement your context-sensitive ICFG traversal here to traverse each program path (once for any loop) from
    /// You will need to collect each path from src node to snk node and then add the path to the `paths` set by
    /// calling the `collectAndTranslatePath` method which is then trigger the path translation.
    /// This implementation, slightly different from Assignment-1, requires ICFGNode* as the first argument.
    '''
    def reachability(self, cur_edge: pysvf.IntraCFGEdge, sink: pysvf.ICFGNode) -> None:
        pass

        '''
    /// TODO: collect each path once this method is called during reachability analysis, and
    /// Collect each program path from the entry to each assertion of the program. In this function,
    /// you will need (1) add each path into the paths set, (2) call translatePath to convert each path into Z3 expressions.
    /// Note that translatePath returns true if the path is feasible, false if the path is infeasible. (3) If a path is feasible,
    /// you will need to call assertchecking to verify the assertion (which is the last ICFGNode of this path).
    '''
    def collect_and_translate_path(self, path: list) -> None:
        pass

# Example usage
if __name__ == "__main__":
    # check sys.argv and print friendly error message if not enough arguments
    if len(sys.argv) != 2:
        print("Usage: python3 Assignment-4.py <path-to-bc-file>")
        sys.exit(1)
    bc_file = sys.argv[1]
    pag = pysvf.get_pag(bc_file)
    pag.get_icfg().dump("icfg")
    ass4 = Assignment4(pag)
    ass4.analyse()
