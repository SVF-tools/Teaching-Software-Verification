#ifndef TEACHING_SVF_COMPAT_H
#define TEACHING_SVF_COMPAT_H

#if __has_include("SVF-LLVM/PAGBuilder.h")
#include "SVF-LLVM/PAGBuilder.h"
namespace SVF {
using TeachingPAGBuilder = PAGBuilder;
inline void releaseTeachingPAG() { PAG::releasePAG(); }
}
#else
#include "SVF-LLVM/SVFIRBuilder.h"
namespace SVF {
using TeachingPAGBuilder = SVFIRBuilder;
inline void releaseTeachingPAG() { SVFIR::releaseSVFIR(); }
}
#endif

#endif
