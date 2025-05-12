import z3
import pysvf
import sys
class Z3Mgr:
    def __init__(self, svfir: pysvf.SVFIR) -> None:
        self.pag = svfir

        self.ctx = z3.Context()
        self.solver = z3.Solver(ctx=self.ctx)
        self.varIdToExprMap = {}
        self.maxNumOfExpr = svfir.getPAGNodeNum()*10
        self.currentExprIdx = 0

        self.addressMask = 0x7f000000
        self.flippedAddressMask = (self.addressMask^0xffffffff)

        indexSort = z3.IntSort(self.ctx)
        elementSort = z3.IntSort(self.ctx)
        arraySort = z3.ArraySort(indexSort, elementSort)
        self.locToValMap = z3.Const('loc2ValMap', arraySort)

    def getInternalId(self, addr: int) -> int:
        return addr & self.flippedAddressMask

    def createExprForObjVar(self, objVar: pysvf.ObjVar) -> z3.ExprRef:
        baseObjVar = self.pag.getBaseObject(objVar.getId())
        if baseObjVar.isConstDataOrAggData() or baseObjVar.isConstantArray() or baseObjVar.isConstantStruct():
            if baseObjVar.isConstIntObjVar():
                obj = baseObjVar.asConstIntObjVar()
                return z3.IntVal(obj.getSExtValue(), self.ctx)
            elif baseObjVar.asConstData().isConstFPObjVar():
                obj = baseObjVar.asConstData().asConstFPObjVar()
                return z3.IntVal(obj.getFPValue(), self.ctx)
            elif baseObjVar.isGlobalObjVar():
                return z3.IntVal(self.getVirtualMemAddress(objVar.getId()), self.ctx)
            elif baseObjVar.isConstantArray() or baseObjVar.isConstantStruct():
                assert False, "implement this part"
            else:
                assert False, "what other types of values we have?"
        else:
            return z3.IntVal(self.getVirtualMemAddress(objVar.getId()), self.ctx)


    def storeValue(self, loc: z3.ExprRef, value: z3.ExprRef) -> z3.ExprRef:
        deref = self.getEvalExpr(loc)
        assert self.isVirtualMemAddress(deref.as_long()), "Pointer operand is not a physical address"
        self.locToValMap = z3.Store(self.locToValMap, deref, value)
        return self.locToValMap


    def loadValue(self, loc: z3.ExprRef) -> z3.ExprRef:
        deref = self.getEvalExpr(loc)
        assert self.isVirtualMemAddress(deref.as_long()), "Pointer operand is not a physical address"
        return z3.Select(self.locToValMap, deref)

    def getEvalExpr(self, e: z3.ExprRef) -> z3.ExprRef:
        res = self.solver.check()
        assert res != z3.unsat, "unsatisfied constraints! Check your contradictory constraints added to the solver"
        model = self.solver.model()
        return model.eval(e)


    def getZ3Expr(self, idx: int, callingCtx: list) -> z3.ExprRef:
        assert self.getInternalId(idx) == idx, "idx cannot be addressValue > 0x7f000000."
        svfVar = self.pag.getGNode(idx)
        if svfVar.isObjVar():
            return self.createExprForObjVar(svfVar.asObjVar())
        else:
            if not isinstance(svfVar, pysvf.ConstIntValVar) and not isinstance(svfVar, pysvf.ConstIntObjVar):
                pass
            else:
                pass
            name = "ValVar" + str(idx)
            return z3.Int(name, self.ctx)


    def callingCtxToStr(self, callingCtx: list) -> str:
        rawstr = ""
        rawstr += "ctx:[ "
        for node in callingCtx:
            rawstr += str(node.getId()) + " "
        rawstr += "] "
        return rawstr


    def updateZ3Expr(self, idx: int, target: z3.ExprRef) -> None:
        if self.maxNumOfExpr < idx + 1:
            raise IndexError("idx out of bound for map access, increase map size!")
        self.varIdToExprMap[idx] = target

    def getZ3Val(self, val:int) -> z3.ExprRef:
        return z3.IntVal(val, self.ctx)

    def isVirtualMemAddress(self, val: int) -> bool:
        return val > 0 and (val & self.addressMask) == self.addressMask

    def getVirtualMemAddress(self, idx: int) -> int:
        return self.addressMask + idx

    def getMemobjAddress(self, addr: int) -> z3.ExprRef:
        objIdx = self.getInternalId(addr)
        assert(self.pag.getGNode(objIdx).isObjVar()), "Invalid memory object index"
        return self.createExprForObjVar(self.pag.getGNode(objIdx).asObjVar())

    def z3ExprToNumValue(self, expr: z3.ExprRef) -> int:
        val = z3.simplify(self.getEvalExpr(expr))
        if isinstance(val, z3.IntNumRef):
            return val.as_long()
        elif val.is_numeral():
            return val.as_long()
        else:
            assert False, "this expression is not numeral"
            sys.exit(1)

    def getGepobjAddress(self, baseExpr: z3.ExprRef, offset: int) -> z3.ExprRef:

        obj = self.getInternalId(self.z3ExprToNumValue(baseExpr))
        assert(self.pag.getGNode(obj).isObjVar()), "Fail to get the base object address!"
        gepObj = self.pag.getGepObjVar(obj, offset)
        if obj == gepObj:
            return self.createExprForObjVar(self.pag.getGNode(obj).asObjVar())
        else:
            return self.createExprForObjVar(self.pag.getGNode(gepObj).asGepObjVar())


    def getGepOffset(self, gep: pysvf.GepStmt, callingCtx: list) -> int:
        if len(gep.getOffsetVarAndGepTypePairVec()) == 0:
            return gep.getConstantStructFldIdx()
        totalOffset = 0
        for i in range(len(gep.getOffsetVarAndGepTypePairVec()) - 1, -1, -1):
            var = gep.getOffsetVarAndGepTypePairVec()[i][0]
            type = gep.getOffsetVarAndGepTypePairVec()[i][1]
            offset = 0
            if var.isConstIntValVar():
                offset = var.asConstIntValVar().getSExtValue()
            else:
                offset = self.getEvalExpr(self.getZ3Expr(var.getId(), callingCtx)).as_long()
            if type is None:
                totalOffset += offset
                continue
            if type.isPointerType():
                totalOffset += offset * self.pag.getNumOfFlattenElements(gep.getSrcPointeeType())
            else:
                totalOffset += self.pag.getFlattenedElemIdx(type, offset)
        return totalOffset

    def printExprValues(self, callingCtx: list):
        printValMap = {}
        objKeyMap = {}
        valKeyMap = {}
        for nIter in self.pag:
            idx = nIter[0]
            node = nIter[1]
            e = self.getEvalExpr(self.getZ3Expr(idx, callingCtx))
            if z3.is_int_value(e) == False:
                continue
            if isinstance(node, pysvf.ValVar):
                if self.isVirtualMemAddress(e.as_long()):
                    valstr = "\t Value: " + hex(e.as_long()) + "\n"
                else:
                    valstr = "\t Value: " + str(e.as_long()) + "\n"
                printValMap["ValVar" + str(idx)] = valstr
                valKeyMap[idx] = "ValVar" + str(idx)
            else:
                if self.isVirtualMemAddress(e.as_long()):
                    storedValue = self.getEvalExpr(self.loadValue(e))
                    if z3.is_int_value(storedValue) == False:
                        continue
                    if isinstance(storedValue, z3.ExprRef):
                        if self.isVirtualMemAddress(storedValue.as_long()):
                            valstr = "\t Value: " + hex(storedValue.as_long()) + "\n"
                        else:
                            valstr = "\t Value: " + str(storedValue.as_long()) + "\n"
                    else:
                        valstr = "\t Value: NULL" + "\n"
                else:
                    valstr = "\t Value: NULL" + "\n"
                printValMap["ObjVar" + str(idx) + " (0x" + hex(idx) + ") "] = valstr
                objKeyMap[idx] = "ObjVar" + str(idx) + " (0x" + hex(idx) + ") "
        print("\n-----------SVFVar and Value-----------")
        for idx, key in objKeyMap.items():
            val = printValMap[key].strip()
            label = f"ObjVar{idx} (0x{idx:x})"
            print(f"{label:<30} {val}")

        for idx, key in valKeyMap.items():
            val = printValMap[key].strip()
            label = f"ValVar{idx}"
            print(f"{label:<30} {val}")
        print("-----------------------------------------")

    def addToSolver(self, expr: z3.ExprRef) -> None:
        self.solver.add(expr)

    def resetSolver(self) -> None:
        self.solver.reset()
        self.varIdToExprMap = {}
        self.currentExprIdx = 0
        self.locToValMap = z3.Const('loc2ValMap', self.locToValMap.sort())


class Assignment4:
    def __init__(self, svfir: pysvf.SVFIR) -> None:
        self.svfir = svfir
        self.icfg = self.svfir.getICFG()
        self.z3mgr = Z3Mgr(svfir)
        self.callingCtx = []
        self.paths = []

        self.path = []
        self.visited = set()
        self.assertCount = 0

    def getZ3Mgr(self) -> Z3Mgr:
        return self.z3mgr

    def identifySource(self) -> list:
        return [self.icfg.getGlobalICFGNode()]

    def identifySink(self) -> list:
        res = []
        cs = self.svfir.getCallSites()
        for c in cs:
            funcName = c.getCalledFunction().getName()
            if funcName == "assert" or funcName == "svf_assert" or funcName == "sink":
                res.append(c)
        return res

    def isAssertFunc(self, funcName: str) -> bool:
        return funcName == "assert" or funcName == "svf_assert" or funcName == "sink"

    def resetSolver(self) -> None:
        self.z3mgr.resetSolver()
        self.callingCtx = []


    def collectAndTranslatePath(self, path: list) -> None:
        # TODO: Implement path collection and translation
        pass

    def translatePath(self, path: list) -> bool:
        for edge in path:
            if edge.isIntraCFGEdge():
                if not self.handleIntra(edge):
                    return False
            elif edge.isCallCFGEdge():
                self.handleCall(edge)
            elif edge.isRetCFGEdge():
                self.handleRet(edge)
            else:
                assert False, "what other edges we have?"
        return True


    def assertChecking(self, inode: pysvf.ICFGNode) -> bool:
        self.assertCount += 1
        callnode = inode
        assert callnode and self.isAssertFunc(callnode.getCalledFunction().getName()) and "last node is not an assert call?"
        print(f"## Analyzing {callnode}")
        arg0 = self.z3mgr.getZ3Expr(callnode.getActualParms()[0].getId(), self.callingCtx)
        self.z3mgr.solver.push()
        self.z3mgr.addToSolver(arg0 == self.z3mgr.getZ3Val(0))

        if self.z3mgr.solver.check() != z3.unsat:
            self.z3mgr.solver.pop()
            self.z3mgr.printExprValues(self.callingCtx)
            ss = f"The assertion is unsatisfiable!! ({inode})"
            ss += f"Counterexample: {self.z3mgr.solver.model()}"
            print(ss)
            print(self.z3mgr.solver)
            assert False
        else:
            self.z3mgr.solver.pop()
            self.z3mgr.printExprValues(self.callingCtx)
            print(self.z3mgr.solver)
            ss = f"The assertion is successfully verified!! ({inode})"
            print(ss)
            return True

    def pushCallingCtx(self, c: pysvf.ICFGNode) -> None:
        self.callingCtx.append(c)

    def popCallingCtx(self) -> None:
        self.callingCtx.pop()


    def handleCall(self, edge: pysvf.CallCFGEdge) -> None:
        # TODO: Implement handling of function calls
        pass


    def handleRet(self, edge: pysvf.RetCFGEdge) -> None:
        # TODO: Implement handling of function returns
        pass


    def handleBranch(self, edge: pysvf.IntraCFGEdge) -> bool:
        assert edge.getCondition() and "not a conditional control-flow transfer?"
        cond = self.z3mgr.getZ3Expr(edge.getCondition().getId(), self.callingCtx)
        successorVal = self.z3mgr.getZ3Val(edge.getSuccessorCondValue())
        self.z3mgr.solver.push()
        self.z3mgr.addToSolver(cond == successorVal)
        res = self.z3mgr.solver.check()
        self.z3mgr.solver.pop()
        if res == z3.unsat:
            print("This conditional ICFGEdge is infeasible!!")
            return False
        else:
            print("This conditional ICFGEdge is feasible")
            self.z3mgr.addToSolver(cond == successorVal)
            return True

    def handleIntra(self, edge: pysvf.IntraCFGEdge) -> bool:
        if edge.getCondition():
            if self.handleBranch(edge) is False:
                return False

        dstNode = edge.getDstNode()
        srcNode = edge.getSrcNode()
        for stmt in dstNode.getSVFStmts():
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
                stmt = stmt.asCmpStmt()
                op0 = self.z3mgr.getZ3Expr(stmt.getOpVar(0).getId(), self.callingCtx)
                op1 = self.z3mgr.getZ3Expr(stmt.getOpVar(1).getId(), self.callingCtx)
                res = self.z3mgr.getZ3Expr(stmt.getResId(), self.callingCtx)
                predicate = stmt.getPredicate()
                if predicate == pysvf.Predicate.ICMP_EQ:
                    self.z3mgr.addToSolver(res == z3.If(op0 == op1, 1, 0))
                elif predicate == pysvf.Predicate.ICMP_NE:
                    self.z3mgr.addToSolver(res == z3.If(op0 != op1, 1, 0))
                elif predicate == pysvf.Predicate.ICMP_UGT or predicate == pysvf.Predicate.ICMP_SGT:
                    self.z3mgr.addToSolver(res == z3.If(op0 > op1, 1, 0))
                elif predicate == pysvf.Predicate.ICMP_UGE or predicate == pysvf.Predicate.ICMP_SGE:
                    self.z3mgr.addToSolver(res == z3.If(op0 >= op1, 1, 0))
                elif predicate == pysvf.Predicate.ICMP_ULT or predicate == pysvf.Predicate.ICMP_SLT:
                    self.z3mgr.addToSolver(res == z3.If(op0 < op1, 1, 0))
                elif predicate == pysvf.Predicate.ICMP_ULE or predicate == pysvf.Predicate.ICMP_SLE:
                    self.z3mgr.addToSolver(res == z3.If(op0 <= op1, 1, 0))
                else:
                    assert False, "implement this part"
            elif isinstance(stmt, pysvf.BinaryOPStmt):
                stmt = stmt.asBinaryOpStmt()
                op0 = self.z3mgr.getZ3Expr(stmt.getOpVar(0).getId(), self.callingCtx)
                op1 = self.z3mgr.getZ3Expr(stmt.getOpVar(1).getId(), self.callingCtx)
                res = self.z3mgr.getZ3Expr(stmt.getResId(), self.callingCtx)
                opcode = stmt.getOpcode()
                if opcode == pysvf.OpCode.Add:
                    self.z3mgr.addToSolver(res == op0 + op1)
                elif opcode == pysvf.OpCode.Sub:
                    self.z3mgr.addToSolver(res == op0 - op1)
                elif opcode == pysvf.OpCode.Mul:
                    self.z3mgr.addToSolver(res == op0 * op1)
                elif opcode == pysvf.OpCode.SDiv:
                    self.z3mgr.addToSolver(res == op0 / op1)
                elif opcode == pysvf.OpCode.SRem:
                    self.z3mgr.addToSolver(res == op0 % op1)
                elif opcode == pysvf.OpCode.Xor:
                    self.z3mgr.addToSolver(res == z3.bv2int(z3.int2bv(32, op0) ^ z3.int2bv(32, op1), 1))
                elif opcode == pysvf.OpCode.And:
                    self.z3mgr.addToSolver(res == z3.bv2int(z3.int2bv(32, op0) & z3.int2bv(32, op1), 1))
                elif opcode == pysvf.OpCode.Or:
                    self.z3mgr.addToSolver(res == z3.bv2int(z3.int2bv(32, op0) | z3.int2bv(32, op1), 1))
                elif opcode == pysvf.OpCode.AShr:
                    self.z3mgr.addToSolver(res == z3.bv2int(z3.ashr(z3.int2bv(32, op0), z3.int2bv(32, op1)), 1))
                elif opcode == pysvf.OpCode.Shl:
                    self.z3mgr.addToSolver(res == z3.bv2int(z3.shl(z3.int2bv(32, op0), z3.int2bv(32, op1)), 1))
                else:
                    assert False, "implement this part"
            elif isinstance(stmt, pysvf.BranchStmt):
                pass

            elif isinstance(stmt, pysvf.PhiStmt):
                stmt = stmt.asPhiStmt()
                res = self.z3mgr.getZ3Expr(stmt.getResId(), self.callingCtx)
                opINodeFound = False
                for i in range(stmt.getOpVarNum()):
                    assert srcNode and "we don't have a predecessor ICFGNode?"
                    if srcNode.getFun().postDominate(srcNode.getBB(), stmt.getOpICFGNode(i).getBB()):
                        ope = self.z3mgr.getZ3Expr(stmt.getOpVar(i).getId(), self.callingCtx)
                        self.z3mgr.addToSolver(res == ope)
                        opINodeFound = True
                assert opINodeFound and "predecessor ICFGNode of this PhiStmt not found?"

        return True


    def analyse(self) -> None:
        for src in self.identifySource():
            assert isinstance(src, pysvf.GlobalICFGNode) and "reachability should start with GlobalICFGNode!"
            for sink in self.identifySink():
                self.reachability(pysvf.IntraCFGEdge(None, src), sink)
                self.resetSolver()


    def reachability(self, curEdge: pysvf.IntraCFGEdge, sink: pysvf.ICFGNode) -> None:
        # TODO: Implement reachability analysis
        pass

# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 Assignment-4.py <path-to-bc-file>")
        sys.exit(1)
    bcFile = sys.argv[1]
    pag = pysvf.getPAG(bcFile)
    pag.getICFG().dump("icfg")

    ass4 = Assignment4(pag)
    ass4.analyse()
    if ass4.assertCount == 0:
        print("No assertion was checked!")
        sys.exit(1)
