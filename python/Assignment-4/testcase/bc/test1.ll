; ModuleID = './test1.ll'
source_filename = "./test1.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"
target triple = "arm64-apple-macosx14.0.0"

; Function Attrs: noinline nounwind ssp uwtable(sync)
define i32 @main() #0 !dbg !9 {
entry:
  %a = alloca [3 x [3 x i32]], align 4
  call void @llvm.dbg.declare(metadata ptr %a, metadata !15, metadata !DIExpression()), !dbg !19
  %arrayidx = getelementptr inbounds [3 x [3 x i32]], ptr %a, i64 0, i64 0, !dbg !20
  %arrayidx1 = getelementptr inbounds [3 x i32], ptr %arrayidx, i64 0, i64 0, !dbg !20
  store i32 0, ptr %arrayidx1, align 4, !dbg !21
  %arrayidx2 = getelementptr inbounds [3 x [3 x i32]], ptr %a, i64 0, i64 0, !dbg !22
  %arrayidx3 = getelementptr inbounds [3 x i32], ptr %arrayidx2, i64 0, i64 1, !dbg !22
  store i32 1, ptr %arrayidx3, align 4, !dbg !23
  %arrayidx4 = getelementptr inbounds [3 x [3 x i32]], ptr %a, i64 0, i64 0, !dbg !24
  %arrayidx5 = getelementptr inbounds [3 x i32], ptr %arrayidx4, i64 0, i64 2, !dbg !24
  store i32 2, ptr %arrayidx5, align 4, !dbg !25
  %arrayidx6 = getelementptr inbounds [3 x [3 x i32]], ptr %a, i64 0, i64 1, !dbg !26
  %arrayidx7 = getelementptr inbounds [3 x i32], ptr %arrayidx6, i64 0, i64 0, !dbg !26
  store i32 3, ptr %arrayidx7, align 4, !dbg !27
  %arrayidx8 = getelementptr inbounds [3 x [3 x i32]], ptr %a, i64 0, i64 1, !dbg !28
  %arrayidx9 = getelementptr inbounds [3 x i32], ptr %arrayidx8, i64 0, i64 1, !dbg !28
  store i32 4, ptr %arrayidx9, align 4, !dbg !29
  %arrayidx10 = getelementptr inbounds [3 x [3 x i32]], ptr %a, i64 0, i64 1, !dbg !30
  %arrayidx11 = getelementptr inbounds [3 x i32], ptr %arrayidx10, i64 0, i64 2, !dbg !30
  store i32 5, ptr %arrayidx11, align 4, !dbg !31
  %arrayidx12 = getelementptr inbounds [3 x [3 x i32]], ptr %a, i64 0, i64 2, !dbg !32
  %arrayidx13 = getelementptr inbounds [3 x i32], ptr %arrayidx12, i64 0, i64 0, !dbg !32
  store i32 6, ptr %arrayidx13, align 4, !dbg !33
  %arrayidx14 = getelementptr inbounds [3 x [3 x i32]], ptr %a, i64 0, i64 2, !dbg !34
  %arrayidx15 = getelementptr inbounds [3 x i32], ptr %arrayidx14, i64 0, i64 1, !dbg !34
  store i32 7, ptr %arrayidx15, align 4, !dbg !35
  %arrayidx16 = getelementptr inbounds [3 x [3 x i32]], ptr %a, i64 0, i64 2, !dbg !36
  %arrayidx17 = getelementptr inbounds [3 x i32], ptr %arrayidx16, i64 0, i64 2, !dbg !36
  store i32 8, ptr %arrayidx17, align 4, !dbg !37
  call void @llvm.dbg.value(metadata i32 2, metadata !38, metadata !DIExpression()), !dbg !39
  call void @llvm.dbg.value(metadata i32 2, metadata !40, metadata !DIExpression()), !dbg !39
  %idxprom = sext i32 2 to i64, !dbg !41
  %arrayidx18 = getelementptr inbounds [3 x [3 x i32]], ptr %a, i64 0, i64 %idxprom, !dbg !41
  %idxprom19 = sext i32 2 to i64, !dbg !41
  %arrayidx20 = getelementptr inbounds [3 x i32], ptr %arrayidx18, i64 0, i64 %idxprom19, !dbg !41
  %0 = load i32, ptr %arrayidx20, align 4, !dbg !41
  %cmp = icmp eq i32 %0, 8, !dbg !42
  call void @svf_assert(i1 noundef zeroext %cmp), !dbg !43
  ret i32 0, !dbg !44
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

declare void @svf_assert(i1 noundef zeroext) #2

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare void @llvm.dbg.value(metadata, metadata, metadata) #1

attributes #0 = { noinline nounwind ssp uwtable(sync) "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+crc,+crypto,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+lse,+neon,+ras,+rcpc,+rdm,+sha2,+sha3,+sm4,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+crc,+crypto,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+lse,+neon,+ras,+rcpc,+rdm,+sha2,+sha3,+sm4,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4, !5, !6, !7}
!llvm.ident = !{!8}

!0 = distinct !DICompileUnit(language: DW_LANG_C11, file: !1, producer: "Homebrew clang version 16.0.6", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, splitDebugInlining: false, nameTableKind: None, sysroot: "/Library/Developer/CommandLineTools/SDKs/MacOSX14.sdk", sdk: "MacOSX14.sdk")
!1 = !DIFile(filename: "test1.c", directory: "/Users/z5489735/2023/0522/Software-Security-Analysis/Assignment-2/Tests/testcases/sse")
!2 = !{i32 7, !"Dwarf Version", i32 4}
!3 = !{i32 2, !"Debug Info Version", i32 3}
!4 = !{i32 1, !"wchar_size", i32 4}
!5 = !{i32 8, !"PIC Level", i32 2}
!6 = !{i32 7, !"uwtable", i32 1}
!7 = !{i32 7, !"frame-pointer", i32 1}
!8 = !{!"Homebrew clang version 16.0.6"}
!9 = distinct !DISubprogram(name: "main", scope: !10, file: !10, line: 8, type: !11, scopeLine: 8, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !14)
!10 = !DIFile(filename: "./test1.c", directory: "/Users/z5489735/2023/0522/Software-Security-Analysis/Assignment-2/Tests/testcases/sse")
!11 = !DISubroutineType(types: !12)
!12 = !{!13}
!13 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!14 = !{}
!15 = !DILocalVariable(name: "a", scope: !9, file: !10, line: 9, type: !16)
!16 = !DICompositeType(tag: DW_TAG_array_type, baseType: !13, size: 288, elements: !17)
!17 = !{!18, !18}
!18 = !DISubrange(count: 3)
!19 = !DILocation(line: 9, column: 9, scope: !9)
!20 = !DILocation(line: 10, column: 5, scope: !9)
!21 = !DILocation(line: 10, column: 13, scope: !9)
!22 = !DILocation(line: 11, column: 5, scope: !9)
!23 = !DILocation(line: 11, column: 13, scope: !9)
!24 = !DILocation(line: 12, column: 5, scope: !9)
!25 = !DILocation(line: 12, column: 13, scope: !9)
!26 = !DILocation(line: 13, column: 5, scope: !9)
!27 = !DILocation(line: 13, column: 13, scope: !9)
!28 = !DILocation(line: 14, column: 5, scope: !9)
!29 = !DILocation(line: 14, column: 13, scope: !9)
!30 = !DILocation(line: 15, column: 5, scope: !9)
!31 = !DILocation(line: 15, column: 13, scope: !9)
!32 = !DILocation(line: 16, column: 5, scope: !9)
!33 = !DILocation(line: 16, column: 13, scope: !9)
!34 = !DILocation(line: 17, column: 5, scope: !9)
!35 = !DILocation(line: 17, column: 13, scope: !9)
!36 = !DILocation(line: 18, column: 5, scope: !9)
!37 = !DILocation(line: 18, column: 13, scope: !9)
!38 = !DILocalVariable(name: "b", scope: !9, file: !10, line: 20, type: !13)
!39 = !DILocation(line: 0, scope: !9)
!40 = !DILocalVariable(name: "c", scope: !9, file: !10, line: 20, type: !13)
!41 = !DILocation(line: 21, column: 16, scope: !9)
!42 = !DILocation(line: 21, column: 24, scope: !9)
!43 = !DILocation(line: 21, column: 5, scope: !9)
!44 = !DILocation(line: 22, column: 5, scope: !9)
