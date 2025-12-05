#!/bin/bash
# ============================================================
# WATCH AUTO-SCALING IN REAL-TIME
# Shows HPA and Pod status side-by-side
# ============================================================

echo "═══════════════════════════════════════════════════════════"
echo "  KUBERNETES AUTO-SCALING MONITOR"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Function to display scaling status
display_status() {
    while true; do
        clear
        echo "═══════════════════════════════════════════════════════════"
        echo "  LLM AUTO-SCALING STATUS - $(date '+%H:%M:%S')"
        echo "═══════════════════════════════════════════════════════════"
        echo ""
        
        echo "📊 HORIZONTAL POD AUTOSCALER:"
        echo "────────────────────────────────────────────────────────────"
        kubectl get hpa llm-hpa -o custom-columns=\
NAME:.metadata.name,\
REFERENCE:.spec.scaleTargetRef.name,\
TARGETS:.status.currentMetrics[0].resource.current.averageUtilization,\
MINPODS:.spec.minReplicas,\
MAXPODS:.spec.maxReplicas,\
REPLICAS:.status.currentReplicas 2>/dev/null || echo "HPA not found"
        echo ""
        
        echo "🔄 POD STATUS:"
        echo "────────────────────────────────────────────────────────────"
        kubectl get pods -l app=llm-inference -o custom-columns=\
NAME:.metadata.name,\
STATUS:.status.phase,\
READY:.status.containerStatuses[0].ready,\
RESTARTS:.status.containerStatuses[0].restartCount,\
AGE:.metadata.creationTimestamp 2>/dev/null || echo "No pods found"
        echo ""
        
        echo "📈 RESOURCE USAGE:"
        echo "────────────────────────────────────────────────────────────"
        kubectl top pods -l app=llm-inference 2>/dev/null || echo "Metrics not available yet"
        echo ""
        
        sleep 5
    done
}

display_status
