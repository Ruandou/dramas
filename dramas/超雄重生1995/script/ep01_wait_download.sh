#!/bin/zsh
# Wait and download all EP01 sub-segment videos
cd /Users/leifu/Movies/dramas/darams/超雄重生1995
export ARK_API_KEY="973a9b4b-2975-4e57-ae08-4c18fd2e2f58"
SCRIPT="/Users/leifu/Movies/dramas/mcps/volc-ark/scripts/ark_seedance_video.py"
OUTDIR="assets/generated/EP01"
mkdir -p "$OUTDIR"

SUCCEEDED=0
FAILED=0

wait_and_download() {
    local SEG="$1"
    local TID="$2"
    echo "=== Waiting for $SEG ($TID) ==="
    RESULT=$(python3 "$SCRIPT" wait --task-id "$TID" --max-wait 300 --interval 8 2>&1)
    STATUS=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null)
    
    if [ "$STATUS" = "succeeded" ]; then
        echo "  -> Succeeded, downloading..."
        python3 "$SCRIPT" download --task-id "$TID" -o "$OUTDIR/${SEG}.mp4" 2>&1
        if [ $? -eq 0 ]; then
            SUCCEEDED=$((SUCCEEDED + 1))
            echo "  -> Downloaded: $OUTDIR/${SEG}.mp4"
        else
            echo "  -> Download FAILED for $SEG"
            FAILED=$((FAILED + 1))
        fi
    else
        echo "  -> Status: $STATUS (not succeeded)"
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

wait_and_download "EP01-SEG01a" "cgt-20260523172101-nxcwc"
wait_and_download "EP01-SEG01b" "cgt-20260523172110-mrrg2"
wait_and_download "EP01-SEG02a" "cgt-20260523172120-2dlzr"
wait_and_download "EP01-SEG02b" "cgt-20260523172130-c2pw8"
wait_and_download "EP01-SEG03a" "cgt-20260523172140-97wsb"
wait_and_download "EP01-SEG03b" "cgt-20260523172152-dz8l8"
wait_and_download "EP01-SEG03c" "cgt-20260523172202-h74q8"
wait_and_download "EP01-SEG04a" "cgt-20260523172212-7fjf7"
wait_and_download "EP01-SEG04b" "cgt-20260523172222-hl2xb"
wait_and_download "EP01-SEG05a" "cgt-20260523172233-g8fxr"
wait_and_download "EP01-SEG05b" "cgt-20260523172245-wrmzg"
wait_and_download "EP01-SEG06a" "cgt-20260523172256-gt4k2"
wait_and_download "EP01-SEG06b" "cgt-20260523172307-zldd9"
wait_and_download "EP01-SEG06c" "cgt-20260523172318-kbhhw"
wait_and_download "EP01-SEG07a" "cgt-20260523172330-h95zq"
wait_and_download "EP01-SEG07b" "cgt-20260523172340-27mhh"

echo "=============================="
echo "SUMMARY: $SUCCEEDED succeeded, $FAILED failed out of 16 total"
echo "=============================="
ls -lh "$OUTDIR"/*.mp4 2>/dev/null
