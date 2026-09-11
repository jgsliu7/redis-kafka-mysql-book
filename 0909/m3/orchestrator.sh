#!/usr/bin/env bash
# 并发调度 25 个审查 agent
# - 并发数：3
# - 输出目录：0909/m3/
# - 跳过已有报告的 agent

# set -u  # 关闭：数组下标未定义会报错

PROMPTS_DIR="0909/m3/prompts"
OUT_DIR="0909/m3"
MAX_CONCURRENT=3

mkdir -p "$OUT_DIR"
mkdir -p "$OUT_DIR/logs"

echo "============================================================"
echo "  25-Agent 并发调度器"
echo "  并发数：$MAX_CONCURRENT"
echo "  时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# 待跑清单
ALL_PROMPTS=()
for f in "$PROMPTS_DIR"/*.md; do
  ALL_PROMPTS+=("$f")
done

# 跳过已跑
TO_RUN=()
SKIPPED=()
for prompt in "${ALL_PROMPTS[@]}"; do
  agent=$(basename "$prompt" .md)
  # 报告文件名约定：与 prompt 同名（agent 自己会写到指定位置）
  if [ -f "$OUT_DIR/${agent}.md" ]; then
    SKIPPED+=("$agent")
  else
    TO_RUN+=("$prompt")
  fi
done

echo "  总数：${#ALL_PROMPTS[@]}"
echo "  已完成：${#SKIPPED[@]} (${SKIPPED[*]:-无})"
echo "  待跑：${#TO_RUN[@]}"
echo ""

# 工作池
declare -a ACTIVE_PIDS=()
declare -a ACTIVE_NAMES=()
START_TIME=$(date +%s)

run_one() {
  local prompt_file="$1"
  local agent_name=$(basename "$prompt_file" .md)
  local log_file="$OUT_DIR/logs/${agent_name}.log"

  echo "[START] $agent_name  $(date +%H:%M:%S)"

  pi -p \
    --no-session \
    --approve \
    --append-system-prompt "$(cat "$prompt_file")" \
    "请执行你的审查任务，并把完整报告写到 /Users/liu/dev/demos/redis-kafka-books/${OUT_DIR}/${agent_name}.md（如果失败，也把失败原因写入该文件以便诊断）" \
    > "$log_file" 2>&1

  local rc=$?
  echo "[DONE]  $agent_name  rc=$rc  $(date +%H:%M:%S)  ($(($(date +%s) - START_TIME))s elapsed)"
}

# 主调度循环
for prompt in "${TO_RUN[@]}"; do
  agent=$(basename "$prompt" .md)

  # 控制并发数：等待直到活跃数 < MAX_CONCURRENT
  while true; do
    # 清理已完成的 PID
    NEW_ACTIVE=()
    NEW_NAMES=()
    if [ ${#ACTIVE_PIDS[@]} -gt 0 ]; then
      for i in "${!ACTIVE_PIDS[@]}"; do
        pid=${ACTIVE_PIDS[$i]}
        name=${ACTIVE_NAMES[$i]}
        if kill -0 "$pid" 2>/dev/null; then
          NEW_ACTIVE+=("$pid")
          NEW_NAMES+=("$name")
        fi
      done
    fi
    ACTIVE_PIDS=("${NEW_ACTIVE[@]+"${NEW_ACTIVE[@]}"}")
    ACTIVE_NAMES=("${NEW_NAMES[@]+"${NEW_NAMES[@]}"}")

    if [ ${#ACTIVE_PIDS[@]} -lt $MAX_CONCURRENT ]; then
      break
    fi
    sleep 2
  done

  # 启动新任务
  run_one "$prompt" &
  ACTIVE_PIDS+=($!)
  ACTIVE_NAMES+=("$agent")
done

# 等待所有任务完成
echo ""
echo "所有任务已启动，等待完成..."
wait
TOTAL_TIME=$(($(date +%s) - START_TIME))

echo ""
echo "============================================================"
echo "  调度完成"
echo "  总耗时：${TOTAL_TIME}s ($(($TOTAL_TIME / 60))min)"
echo "============================================================"

# 汇总
echo ""
echo "报告清单："
for prompt in "${ALL_PROMPTS[@]}"; do
  agent=$(basename "$prompt" .md)
  if [ -f "$OUT_DIR/${agent}.md" ]; then
    size=$(wc -c < "$OUT_DIR/${agent}.md" | tr -d ' ')
    echo "  ✅ $agent  (${size} bytes)"
  else
    echo "  ❌ $agent  (缺失)"
  fi
done