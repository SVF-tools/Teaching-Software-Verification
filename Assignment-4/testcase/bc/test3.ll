; ModuleID = '../src/test3.c'
source_filename = "../src/test3.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @test(i32 %a, i32 %b) #0 {
entry:
  %a.addr = alloca i32, align 4
  %b.addr = alloca i32, align 4
  %x = alloca i32, align 4
  %y = alloca i32, align 4
  store i32 %a, i32* %a.addr, align 4
  store i32 %b, i32* %b.addr, align 4
  store i32 1, i32* %x, align 4
  store i32 1, i32* %y, align 4
  %0 = load i32, i32* %a.addr, align 4
  %1 = load i32, i32* %b.addr, align 4
  %cmp = icmp sgt i32 %0, %1
  br i1 %cmp, label %if.then, label %if.else

if.then:                                          ; preds = %entry
  %2 = load i32, i32* %x, align 4
  %inc = add nsw i32 %2, 1
  store i32 %inc, i32* %x, align 4
  %3 = load i32, i32* %y, align 4
  %inc1 = add nsw i32 %3, 1
  store i32 %inc1, i32* %y, align 4
  %4 = load i32, i32* %x, align 4
  %5 = load i32, i32* %y, align 4
  %cmp2 = icmp eq i32 %4, %5
  call void @svf_assert(i1 zeroext %cmp2)
  br label %if.end

if.else:                                          ; preds = %entry
  %6 = load i32, i32* %x, align 4
  %inc3 = add nsw i32 %6, 1
  store i32 %inc3, i32* %x, align 4
  %7 = load i32, i32* %x, align 4
  %cmp4 = icmp eq i32 %7, 2
  call void @svf_assert(i1 zeroext %cmp4)
  br label %if.end

if.end:                                           ; preds = %if.else, %if.then
  ret i32 0
}

declare dso_local void @svf_assert(i1 zeroext) #1

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @main() #0 {
entry:
  %retval = alloca i32, align 4
  %a = alloca i32, align 4
  %b = alloca i32, align 4
  store i32 0, i32* %retval, align 4
  store i32 1, i32* %a, align 4
  store i32 2, i32* %b, align 4
  %0 = load i32, i32* %a, align 4
  %1 = load i32, i32* %b, align 4
  %call = call i32 @test(i32 %0, i32 %1)
  ret i32 0
}

attributes #0 = { noinline nounwind uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"uwtable", i32 1}
!2 = !{i32 7, !"frame-pointer", i32 2}
!3 = !{!"clang version 13.0.0"}
