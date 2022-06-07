; ModuleID = '../src/test1.c'
source_filename = "../src/test1.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @main() #0 {
entry:
  %p = alloca i32*, align 8
  %a = alloca i32, align 4
  store i32 1, i32* %a, align 4
  store i32* %a, i32** %p, align 8
  %0 = load i32*, i32** %p, align 8
  store i32 3, i32* %0, align 4
  %1 = load i32, i32* %a, align 4
  %cmp = icmp eq i32 %1, 3
  call void @svf_assert(i1 zeroext %cmp)
  ret i32 0
}

declare dso_local void @svf_assert(i1 zeroext) #1

attributes #0 = { noinline nounwind uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"uwtable", i32 1}
!2 = !{i32 7, !"frame-pointer", i32 2}
!3 = !{!"clang version 13.0.0"}
