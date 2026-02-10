#!/bin/bash

echo "=========================================="
echo "BTRC Dashboard - Connection Diagnostic"
echo "=========================================="
echo ""

echo "1. Testing Docker Container Status..."
docker ps --filter "name=btrc-v3-nginx" --format "   ✓ {{.Names}}: {{.Status}}"
echo ""

echo "2. Testing Port 9000 Listening..."
if netstat -tuln | grep -q ":9000"; then
    echo "   ✓ Port 9000 is LISTENING"
else
    echo "   ✗ Port 9000 is NOT listening"
fi
echo ""

echo "3. Testing Dashboard Endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/dashboard)
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✓ Dashboard responding: HTTP $HTTP_CODE OK"
else
    echo "   ✗ Dashboard error: HTTP $HTTP_CODE"
fi
echo ""

echo "4. Testing Health Endpoint..."
HEALTH=$(curl -s http://localhost:9000/health)
if [ "$HEALTH" = "OK" ]; then
    echo "   ✓ Health check: $HEALTH"
else
    echo "   ✗ Health check failed: $HEALTH"
fi
echo ""

echo "5. Testing JavaScript File..."
HTTP_CODE_JS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/dashboard.js)
if [ "$HTTP_CODE_JS" = "200" ]; then
    echo "   ✓ JavaScript file: HTTP $HTTP_CODE_JS OK"
else
    echo "   ✗ JavaScript file error: HTTP $HTTP_CODE_JS"
fi
echo ""

echo "6. Testing Metabase Proxy..."
HTTP_CODE_MB=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/)
if [ "$HTTP_CODE_MB" = "200" ] || [ "$HTTP_CODE_MB" = "302" ]; then
    echo "   ✓ Metabase proxy: HTTP $HTTP_CODE_MB OK"
else
    echo "   ✗ Metabase proxy error: HTTP $HTTP_CODE_MB"
fi
echo ""

echo "=========================================="
echo "URLs to Try:"
echo "=========================================="
echo ""
echo "Main Dashboard:"
echo "   http://localhost:9000/dashboard"
echo ""
echo "Health Check:"
echo "   http://localhost:9000/health"
echo ""
echo "Metabase Direct:"
echo "   http://localhost:3000/dashboard/6"
echo ""
echo "=========================================="
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ ALL TESTS PASSED!"
    echo ""
    echo "The server is working correctly."
    echo "If your browser still shows 'connection refused':"
    echo "  1. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)"
    echo "  2. Clear browser cache"
    echo "  3. Try incognito/private mode"
    echo "  4. Try a different browser"
else
    echo "⚠️ TESTS FAILED"
    echo ""
    echo "Please run:"
    echo "  docker-compose restart nginx"
    echo ""
    echo "Then try again."
fi
