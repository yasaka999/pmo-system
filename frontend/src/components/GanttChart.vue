<template>
  <div class="gantt-wrapper">
    <!-- 工具栏 -->
    <div class="gantt-toolbar">
      <span class="gantt-subtitle">共 {{ milestones.length }} 个里程碑，{{ totalTasks }} 个工作项</span>
      <div class="gantt-legend">
        <span class="legend-item"><i class="dot" style="background:#70AD47"></i>已完成</span>
        <span class="legend-item"><i class="dot" style="background:#4472C4"></i>进行中</span>
        <span class="legend-item"><i class="dot" style="background:#FFC000"></i>延期</span>
        <span class="legend-item"><i class="dot" style="background:#E0E0E0"></i>未开始</span>
        <span class="legend-item"><i class="dot diamond" style="background:#2E4057"></i>里程碑</span>
      </div>
    </div>

    <div class="gantt-container" ref="ganttEl">
      <!-- 左侧名称面板 -->
      <div class="gantt-left">
        <!-- 表头占位 -->
        <div class="gantt-header-cell">任务名称</div>
        <!-- 项目行 -->
        <div class="gantt-name-row project-row">
          <span>📁 {{ project.name }}</span>
        </div>
        <!-- 里程碑 + 任务行 -->
        <template v-for="ms in milestones" :key="ms.id">
          <div class="gantt-name-row ms-row">
            <span>◆ {{ ms.name }}</span>
          </div>
          <div v-for="task in tasksByMs(ms.id)" :key="task.id" class="gantt-name-row task-row">
            <span>{{ task.name }}</span>
          </div>
        </template>
      </div>

      <!-- 右侧时间轴 -->
      <div class="gantt-right" ref="timelineEl">
        <!-- 月份表头 -->
        <div class="gantt-header-row">
          <div
            v-for="m in months"
            :key="m.key"
            class="gantt-month-cell"
            :style="{ width: m.widthPx + 'px' }"
          >{{ m.label }}</div>
        </div>

        <!-- 内容区（相对定位容器） -->
        <div class="gantt-body" :style="{ width: totalWidthPx + 'px' }">
          <!-- 今天竖线 -->
          <div v-if="todayLeft >= 0 && todayLeft <= totalWidthPx"
            class="today-line" :style="{ left: todayLeft + 'px' }">
            <span class="today-label">今天</span>
          </div>

          <!-- 月份格线 -->
          <div v-for="m in months" :key="'g'+m.key"
            class="grid-line" :style="{ left: m.leftPx + 'px' }"></div>

          <!-- 项目总条 -->
          <div class="gantt-row project-row">
            <div v-if="projectBar"
              class="gantt-bar project-bar"
              :style="{ left: projectBar.left + 'px', width: projectBar.width + 'px' }"
              :title="`${project.plan_start} → ${project.plan_end}`"
            >
              <span class="bar-label">{{ project.plan_start }} ~ {{ project.plan_end }}</span>
            </div>
          </div>

          <!-- 里程碑 + 任务条 -->
          <template v-for="ms in milestones" :key="'ms'+ms.id">
            <!-- 里程碑行：显示 marker -->
            <div class="gantt-row ms-row">
              <div v-if="msMarker(ms)"
                class="gantt-ms-marker"
                :class="msClass(ms.status)"
                :style="{ left: msMarker(ms) - 7 + 'px' }"
                :title="`${ms.name}  计划: ${ms.plan_date}  实际: ${ms.actual_date || '-'}`">
              </div>
              <!-- 实际完成 marker -->
              <div v-if="ms.actual_date && dateToLeft(ms.actual_date) >= 0"
                class="gantt-ms-marker actual"
                :style="{ left: dateToLeft(ms.actual_date) - 7 + 'px' }">
              </div>
            </div>
            <!-- 任务行 -->
            <div v-for="task in tasksByMs(ms.id)" :key="'t'+task.id" class="gantt-row task-row">
              <div v-if="taskBar(task)"
                class="gantt-bar task-bar"
                :class="taskClass(task.status)"
                :style="{ left: taskBar(task).left + 'px', width: taskBar(task).width + 'px' }"
                :title="`${task.name}  ${task.plan_start} → ${task.plan_end}  完成度: ${task.progress}%`"
              >
                <!-- 完成度覆盖 -->
                <div class="bar-progress" :style="{ width: task.progress + '%' }"></div>
                <span class="bar-label">{{ task.progress }}%</span>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  project: { type: Object, required: true },
  milestones: { type: Array, default: () => [] },
  tasks: { type: Array, default: () => [] },
  dayPx: { type: Number, default: 14 },  // 每天的像素宽度，支持紧凑/标准/宽松
})

const DAY_PX = computed(() => props.dayPx)   // 响应式的每天像素宽度

// ── 日期范围计算 ─────────────────────────────────────
const { startDate, endDate } = computed(() => {
  const dates = []
  if (props.project.plan_start) dates.push(new Date(props.project.plan_start))
  if (props.project.plan_end) dates.push(new Date(props.project.plan_end))
  props.milestones.forEach(ms => {
    if (ms.plan_date) dates.push(new Date(ms.plan_date))
    if (ms.actual_date) dates.push(new Date(ms.actual_date))
  })
  props.tasks.forEach(t => {
    if (t.plan_start) dates.push(new Date(t.plan_start))
    if (t.plan_end) dates.push(new Date(t.plan_end))
  })
  if (!dates.length) {
    const now = new Date()
    return { startDate: new Date(now.getFullYear(), now.getMonth() - 1, 1),
             endDate: new Date(now.getFullYear(), now.getMonth() + 4, 1) }
  }
  let s = new Date(Math.min(...dates))
  let e = new Date(Math.max(...dates))
  // 前后各留 15 天
  s.setDate(s.getDate() - 15)
  e.setDate(e.getDate() + 15)
  s = new Date(s.getFullYear(), s.getMonth(), 1)  // 月初
  e = new Date(e.getFullYear(), e.getMonth() + 1, 1) // 下月初
  return { startDate: s, endDate: e }
}).value

const totalDays = Math.ceil((endDate - startDate) / 86400000)
const totalWidthPx = computed(() => totalDays * DAY_PX.value)

function dateToLeft(dateStr) {
  if (!dateStr) return -1
  const d = new Date(dateStr)
  const diff = Math.floor((d - startDate) / 86400000)
  return diff * DAY_PX.value
}

// ── 月份表头 ─────────────────────────────────────────
const months = computed(() => {
  const result = []
  let cur = new Date(startDate)
  while (cur < endDate) {
    const y = cur.getFullYear()
    const m = cur.getMonth()
    const next = new Date(y, m + 1, 1)
    const end = next < endDate ? next : endDate
    const dayCount = Math.floor((end - cur) / 86400000)
    result.push({
      key: `${y}-${m}`,
      label: `${y}年${m + 1}月`,
      leftPx: Math.floor((cur - startDate) / 86400000) * DAY_PX.value,
      widthPx: dayCount * DAY_PX.value,
    })
    cur = next
  }
  return result
})

// ── 今天线 ──────────────────────────────────────────
const todayLeft = computed(() => {
  const now = new Date()
  now.setHours(0,0,0,0)
  return Math.floor((now - startDate) / 86400000) * DAY_PX.value
})

// ── 项目总条 ─────────────────────────────────────────
const projectBar = computed(() => {
  if (!props.project.plan_start || !props.project.plan_end) return null
  const left = dateToLeft(props.project.plan_start)
  const right = dateToLeft(props.project.plan_end)
  return { left, width: Math.max(right - left, 10) }
})

// ── 里程碑 marker ────────────────────────────────────
function msMarker(ms) {
  if (!ms.plan_date) return null
  return dateToLeft(ms.plan_date)
}

function msClass(status) {
  return {
    'ms_done': 'ms-done',
    'ms_inprog': 'ms-active', '进行中': 'ms-active',
    'ms_delay': 'ms-delay', '延期': 'ms-delay',
    'ms_notstart': 'ms-pending', '未开始': 'ms-pending',
  }[status] || 'ms-pending'
}

// ── 任务条 ───────────────────────────────────────────
function taskBar(task) {
  if (!task.plan_start || !task.plan_end) return null
  const left = dateToLeft(task.plan_start)
  const right = dateToLeft(task.plan_end)
  return { left, width: Math.max(right - left, 10) }
}

function taskClass(status) {
  return {
    '已完成': 'bar-done',
    '进行中': 'bar-active',
    '延期': 'bar-delay',
  }[status] || 'bar-pending'
}

// ── 辅助 ─────────────────────────────────────────────
function tasksByMs(msId) {
  return props.tasks.filter(t => t.milestone_id === msId)
}

const totalTasks = computed(() => props.tasks.length)
</script>

<style scoped>
/* 整体容器 */
.gantt-wrapper {
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
}
.gantt-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #f8fafd;
  border-bottom: 1px solid #e8edf3;
  flex-wrap: wrap;
  gap: 8px;
}
.gantt-subtitle { font-size: 13px; color: #666; }
.gantt-legend { display: flex; gap: 14px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 4px; font-size: 12px; color: #555; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }
.dot.diamond {
  border-radius: 0;
  transform: rotate(45deg);
  width: 9px; height: 9px;
}

/* 主体布局 */
.gantt-container { display: flex; overflow-x: auto; }

/* 左侧名称面板 */
.gantt-left {
  min-width: 200px;
  max-width: 220px;
  flex-shrink: 0;
  border-right: 2px solid #e8edf3;
  background: #fafbfd;
}
.gantt-header-cell {
  height: 36px;
  line-height: 36px;
  padding: 0 12px;
  font-size: 12px;
  font-weight: 600;
  color: #2E4057;
  border-bottom: 1px solid #e0e6f0;
  background: #f0f4fa;
}
.gantt-name-row {
  height: 36px;
  line-height: 36px;
  padding: 0 10px;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  border-bottom: 1px solid #f0f0f0;
}
.gantt-name-row.project-row { background: #e8f0fe; font-weight: 700; color: #2E4057; }
.gantt-name-row.ms-row { background: #f5f7fa; font-weight: 600; color: #4472C4; padding-left: 14px; }
.gantt-name-row.task-row { color: #444; padding-left: 26px; }

/* 右侧时间轴 */
.gantt-right { flex: 1; overflow-x: auto; position: relative; }

.gantt-header-row {
  display: flex;
  height: 36px;
  background: #f0f4fa;
  border-bottom: 1px solid #e0e6f0;
  position: sticky;
  top: 0;
  z-index: 10;
}
.gantt-month-cell {
  flex-shrink: 0;
  height: 36px;
  line-height: 36px;
  padding: 0 6px;
  font-size: 11px;
  font-weight: 600;
  color: #2E4057;
  border-right: 1px solid #dde3ee;
  background: #f0f4fa;
  text-align: center;
}

/* body 相对定位容器 */
.gantt-body { position: relative; min-height: 60px; }

/* 今天竖线 */
.today-line {
  position: absolute;
  top: 0; bottom: 0;
  width: 2px;
  background: #FF4444;
  z-index: 9;
  pointer-events: none;
}
.today-label {
  position: absolute;
  top: -2px;
  left: 3px;
  font-size: 10px;
  color: #FF4444;
  white-space: nowrap;
}

/* 月份格线 */
.grid-line {
  position: absolute;
  top: 0; bottom: 0;
  width: 1px;
  background: #e8edf3;
  pointer-events: none;
}

/* 甘特行 */
.gantt-row {
  height: 36px;
  border-bottom: 1px solid #f0f0f0;
  position: relative;
}
.gantt-row.project-row { background: rgba(68, 114, 196, 0.05); }
.gantt-row.ms-row { background: rgba(68, 114, 196, 0.03); }

/* 项目总条 */
.gantt-bar {
  position: absolute;
  top: 8px;
  height: 18px;
  border-radius: 4px;
  overflow: hidden;
  cursor: default;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12);
}
.project-bar {
  background: linear-gradient(90deg, #2E4057, #4472C4);
  top: 10px;
  height: 16px;
}
.project-bar .bar-label { color: #fff; }

/* 任务条 */
.task-bar { top: 7px; height: 20px; }
.bar-progress {
  position: absolute;
  top: 0; left: 0; bottom: 0;
  background: rgba(255,255,255,0.25);
  border-radius: 4px 0 0 4px;
}
.bar-label {
  position: absolute;
  top: 50%;
  left: 6px;
  transform: translateY(-50%);
  font-size: 11px;
  color: #fff;
  pointer-events: none;
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}
.bar-done    { background: linear-gradient(90deg, #52b355, #70AD47); }
.bar-active  { background: linear-gradient(90deg, #3060c4, #4472C4); }
.bar-delay   { background: linear-gradient(90deg, #e05a3a, #FFA07A); }
.bar-pending { background: linear-gradient(90deg, #bbb, #ccc); }

/* 里程碑菱形 marker */
.gantt-ms-marker {
  position: absolute;
  top: 10px;
  width: 14px;
  height: 14px;
  transform: rotate(45deg);
  border-radius: 2px;
  border: 2px solid #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  z-index: 5;
}
.gantt-ms-marker.actual {
  background: #fff;
  border: 2px solid #70AD47;
}
.ms-done    { background: #70AD47; }
.ms-active  { background: #4472C4; }
.ms-delay   { background: #FFC000; }
.ms-pending { background: #aaa; }
</style>
