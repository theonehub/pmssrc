#!/bin/bash

echo "📊 PMS Frontend Enhancement Progress Report"
echo "=========================================="
echo ""

# Count TypeScript files
TS_FILES=$(find src -name "*.ts" -o -name "*.tsx" | wc -l | tr -d ' ')
JS_FILES=$(find src -name "*.js" -o -name "*.jsx" | wc -l | tr -d ' ')
TOTAL_FILES=$((TS_FILES + JS_FILES))

echo "📁 File Conversion Progress:"
echo "   TypeScript files: $TS_FILES"
echo "   JavaScript files: $JS_FILES"
echo "   Total files: $TOTAL_FILES"
echo "   Conversion rate: $(echo "scale=1; $TS_FILES * 100 / $TOTAL_FILES" | bc)%"
echo ""

# Check linting warnings
echo "🔍 Code Quality Check:"
LINT_OUTPUT=$(npm run lint 2>&1)
WARNING_COUNT=$(echo "$LINT_OUTPUT" | grep -c "warning")
ERROR_COUNT=$(echo "$LINT_OUTPUT" | grep -c "error")

echo "   Linting warnings: $WARNING_COUNT"
echo "   Linting errors: $ERROR_COUNT"
echo ""

# TypeScript compilation
echo "🔧 TypeScript Compilation:"
if npm run type-check > /dev/null 2>&1; then
    echo "   ✅ TypeScript compilation: PASSED"
else
    echo "   ❌ TypeScript compilation: FAILED"
fi
echo ""

# Security check
echo "🛡️ Security Status:"
AUDIT_OUTPUT=$(npm audit --audit-level=high 2>&1)
if echo "$AUDIT_OUTPUT" | grep -q "found 0 vulnerabilities"; then
    echo "   ✅ No high/critical vulnerabilities"
else
    HIGH_VULN=$(echo "$AUDIT_OUTPUT" | grep -o "[0-9]* high" | head -1 | cut -d' ' -f1)
    CRITICAL_VULN=$(echo "$AUDIT_OUTPUT" | grep -o "[0-9]* critical" | head -1 | cut -d' ' -f1)
    echo "   ⚠️ High vulnerabilities: ${HIGH_VULN:-0}"
    echo "   🚨 Critical vulnerabilities: ${CRITICAL_VULN:-0}"
fi
echo ""

# Progress summary
echo "🎯 Phase 1 Goals:"
echo "   Target: <50 linting warnings (Current: $WARNING_COUNT)"
echo "   Target: 20+ TypeScript files (Current: $TS_FILES)"
echo "   Target: 0 high/critical vulnerabilities"
echo ""

# Next steps
echo "📋 Next Steps:"
if [ $TS_FILES -lt 10 ]; then
    echo "   1. Continue converting utility files and hooks to TypeScript"
elif [ $TS_FILES -lt 20 ]; then
    echo "   1. Convert key components (Login, UsersList, etc.) to TypeScript"
else
    echo "   1. Focus on removing console.log statements and unused imports"
fi

if [ $WARNING_COUNT -gt 100 ]; then
    echo "   2. Remove unused imports and variables"
elif [ $WARNING_COUNT -gt 50 ]; then
    echo "   2. Remove console.log statements"
else
    echo "   2. Add unit tests for converted components"
fi

echo "   3. Run: npm run lint:fix to auto-fix issues"
echo "   4. Run: npm run format to ensure consistent formatting" 