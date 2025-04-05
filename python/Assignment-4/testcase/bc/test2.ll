; ModuleID = './test2.ll'
source_filename = "./test2.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"
target triple = "arm64-apple-macosx14.0.0"

; Function Attrs: noinline nounwind ssp uwtable(sync)
define i32 @getValue(ptr noundef %arr, i32 noundef %idx) #0 !dbg !9 {
entry:
  call void @llvm.dbg.value(metadata ptr %arr, metadata !16, metadata !DIExpression()), !dbg !17
  call void @llvm.dbg.value(metadata i32 %idx, metadata !18, metadata !DIExpression()), !dbg !17
  %idxprom = sext i32 %idx to i64, !dbg !19
  %arrayidx = getelementptr inbounds i32, ptr %arr, i64 %idxprom, !dbg !19
  %0 = load i32, ptr %arrayidx, align 4, !dbg !19
  ret i32 %0, !dbg !20
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

; Function Attrs: noinline nounwind ssp uwtable(sync)
define i32 @main() #0 !dbg !21 {
entry:
  %arr = alloca [2 x i32], align 4
  call void @llvm.dbg.declare(metadata ptr %arr, metadata !24, metadata !DIExpression()), !dbg !28
  %arrayidx = getelementptr inbounds [2 x i32], ptr %arr, i64 0, i64 0, !dbg !29
  store i32 0, ptr %arrayidx, align 4, !dbg !30
  %arrayidx1 = getelementptr inbounds [2 x i32], ptr %arr, i64 0, i64 1, !dbg !31
  store i32 1, ptr %arrayidx1, align 4, !dbg !32
  %arraydecay = getelementptr inbounds [2 x i32], ptr %arr, i64 0, i64 0, !dbg !33
  %call = call i32 @getValue(ptr noundef %arraydecay, i32 noundef 1), !dbg !34
  call void @llvm.dbg.value(metadata i32 %call, metadata !35, metadata !DIExpression()), !dbg !36
  %cmp = icmp eq i32 %call, 1, !dbg !37
  call void @svf_assert(i1 noundef zeroext %cmp), !dbg !38
  ret i32 0, !dbg !39
}

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
!1 = !DIFile(filename: "test2.c", directory: "/Users/z5489735/2023/0522/Software-Security-Analysis/Assignment-2/Tests/testcases/sse")
!2 = !{i32 7, !"Dwarf Version", i32 4}
!3 = !{i32 2, !"Debug Info Version", i32 3}
!4 = !{i32 1, !"wchar_size", i32 4}
!5 = !{i32 8, !"PIC Level", i32 2}
!6 = !{i32 7, !"uwtable", i32 1}
!7 = !{i32 7, !"frame-pointer", i32 1}
!8 = !{!"Homebrew clang version 16.0.6"}
!9 = distinct !DISubprogram(name: "getValue", scope: !10, file: !10, line: 8, type: !11, scopeLine: 8, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !15)
!10 = !DIFile(filename: "./test2.c", directory: "/Users/z5489735/2023/0522/Software-Security-Analysis/Assignment-2/Tests/testcases/sse")
!11 = !DISubroutineType(types: !12)
!12 = !{!13, !14, !13}
!13 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!14 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !13, size: 64)
!15 = !{}
!16 = !DILocalVariable(name: "arr", arg: 1, scope: !9, file: !10, line: 8, type: !14)
!17 = !DILocation(line: 0, scope: !9)
!18 = !DILocalVariable(name: "idx", arg: 2, scope: !9, file: !10, line: 8, type: !13)
!19 = !DILocation(line: 9, column: 12, scope: !9)
!20 = !DILocation(line: 9, column: 5, scope: !9)
!21 = distinct !DISubprogram(name: "main", scope: !10, file: !10, line: 12, type: !22, scopeLine: 12, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !15)
!22 = !DISubroutineType(types: !23)
!23 = !{!13}
!24 = !DILocalVariable(name: "arr", scope: !21, file: !10, line: 13, type: !25)
!25 = !DICompositeType(tag: DW_TAG_array_type, baseType: !13, size: 64, elements: !26)
!26 = !{!27}
!27 = !DISubrange(count: 2)
!28 = !DILocation(line: 13, column: 9, scope: !21)
!29 = !DILocation(line: 14, column: 5, scope: !21)
!30 = !DILocation(line: 14, column: 12, scope: !21)
!31 = !DILocation(line: 15, column: 5, scope: !21)
!32 = !DILocation(line: 15, column: 12, scope: !21)
!33 = !DILocation(line: 16, column: 22, scope: !21)
!34 = !DILocation(line: 16, column: 13, scope: !21)
!35 = !DILocalVariable(name: "v", scope: !21, file: !10, line: 16, type: !13)
!36 = !DILocation(line: 0, scope: !21)
!37 = !DILocation(line: 17, column: 18, scope: !21)
!38 = !DILocation(line: 17, column: 5, scope: !21)
!39 = !DILocation(line: 18, column: 5, scope: !21)
