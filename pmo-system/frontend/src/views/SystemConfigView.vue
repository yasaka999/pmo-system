<template>
  <div>
    <!-- 页面头部 -->
    <div class="config-header">
      <div>
        <h2 class="page-title">系统配置</h2>
        <p class="page-subtitle">管理系统中所有可配置的选项和字段</p>
      </div>
      <el-button type="primary" :loading="saving" @click="saveAll" size="large">
        <el-icon><Check /></el-icon> 保存所有配置
      </el-button>
    </div>

    <!-- Tab 页 -->
    <div class="page-card">
      <el-tabs v-model="activeTab" class="config-tabs">

        <!-- ── 项目配置 ── -->
        <el-tab-pane label="项目配置" name="project">
          <div class="section-group">
            <ConfigSection
              title="项目阶段"
              desc="项目生命周期阶段选项（点击颜色圆点可设置标签颜色）"
              :items="getItems('project_phase')"
              show-color
              @add="(label) => addItem('project_phase', label)"
              @remove="removeItem"
            />
            <el-divider />
            <ConfigSection
              title="项目状态"
              desc="项目状态选项（点击颜色圆点可设置标签颜色）"
              :items="getItems('project_status')"
              show-color
              @add="(label) => addItem('project_status', label)"
              @remove="removeItem"
            />
          </div>
        </el-tab-pane>

        <!-- ── 问题配置 ── -->
        <el-tab-pane label="问题配置" name="issue">
          <div class="section-group">
            <ConfigSection
              title="严重等级"
              desc="问题严重程度分级选项"
              :items="getItems('issue_severity')"
              show-color
              @add="(label) => addItem('issue_severity', label)"
              @remove="removeItem"
            />
            <el-divider />
            <ConfigSection
              title="问题状态"
              desc="问题处理进度状态选项"
              :items="getItems('issue_status')"
              show-color
              @add="(label) => addItem('issue_status', label)"
              @remove="removeItem"
            />
            <el-divider />
            <ConfigSection
              title="问题来源"
              desc="问题的发现或来源方"
              :items="getItems('issue_source')"
              @add="(label) => addItem('issue_source', label)"
              @remove="removeItem"
            />
          </div>
        </el-tab-pane>

        <!-- ── 风险配置 ── -->
        <el-tab-pane label="风险配置" name="risk">
          <div class="section-group">
            <ConfigSection
              title="风险概率"
              desc="风险发生可能性等级选项"
              :items="getItems('risk_prob')"
              show-color
              @add="(label) => addItem('risk_prob', label)"
              @remove="removeItem"
            />
            <el-divider />
            <ConfigSection
              title="影响程度"
              desc="风险对项目的影响等级选项"
              :items="getItems('risk_impact')"
              show-color
              @add="(label) => addItem('risk_impact', label)"
              @remove="removeItem"
            />
            <el-divider />
            <ConfigSection
              title="风险状态"
              desc="风险应对处理状态选项"
              :items="getItems('risk_status')"
              show-color
              @add="(label) => addItem('risk_status', label)"
              @remove="removeItem"
            />
          </div>
        </el-tab-pane>

        <!-- ── 其他配置 ── -->
        <el-tab-pane label="其他配置" name="other">
          <div class="section-group">
            <ConfigSection
              title="里程碑状态"
              desc="里程碑和工作任务的进度状态选项"
              :items="getItems('milestone_status')"
              show-color
              @add="(label) => addItem('milestone_status', label)"
              @remove="removeItem"
            />
          </div>
        </el-tab-pane>

        <!-- ── 看板设置 ── -->
        <el-tab-pane label="看板设置" name="widgets">
          <div class="section-group">
            <h3 class="section-title">总览看板卡片配置</h3>
            <p class="section-desc" style="margin-bottom:16px">
              控制项目总览页面显示哪些点击看板。开关控制显示/隐藏，按面按针调整顺序。保存后刷新总览页即可生效。
            </p>
            <div class="widget-config-list">
              <div
                v-for="(w, idx) in widgetItems"
                :key="w.code"
                class="widget-config-row"
              >
                <span class="widget-order">{{ idx + 1 }}</span>
                <span class="widget-name">{{ w.label }}</span>
                <div class="widget-actions">
                  <el-switch
                    v-model="w.is_active"
                    :active-text="w.is_active ? '显示' : '隐藏'"
                    style="margin-right:12px"
                  />
                  <el-button-group size="small">
                    <el-button :disabled="idx === 0" @click="moveWidget(idx, -1)">↑</el-button>
                    <el-button :disabled="idx === widgetItems.length - 1" @click="moveWidget(idx, 1)">↓</el-button>
                  </el-button-group>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { dictApi } from '@/api'
import { ElMessage } from 'element-plus'
import ConfigSection from '@/components/ConfigSection.vue'

const activeTab = ref('project')
const saving = ref(false)

// 看板配置项（dashboard_widget 分类）
const WIDGET_LABELS = {
  total: '项目总数', in_progress: '进行中', done: '已完成',
  open_issues: '未关闭问题', open_risks: '开放风险',
  pending_delivery: '待交付', delivered: '已交付',
  pending_acceptance: '待验收', accepted: '已验收',
  status_normal: '状态：正常', status_warning: '状态：预警',
  status_delayed: '状态：延期', status_paused: '状态：暂停',
  status_done: '状态：已完成',
}
const widgetItems = reactive([])   // { id, code, label, is_active, sort_order }

// 所有字典项的扁平列表（响应式）
// 每条记录附加 _deleted / _new 标记，不直接修改后端，点"保存"时批量提交
const allItems = reactive([])

onMounted(async () => {
  try {
    const data = await dictApi.list()
    allItems.splice(0, allItems.length, ...data.map(d => ({ ...d, _deleted: false, _new: false })))
    // 单独提取 widget 配置，按 sort_order 排序
    const ws = data.filter(d => d.category === 'dashboard_widget')
      .sort((a, b) => a.sort_order - b.sort_order)
    widgetItems.splice(0, widgetItems.length, ...ws.map(w => ({
      id: w.id, code: w.code,
      label: WIDGET_LABELS[w.code] || w.label,
      is_active: w.is_active,
      sort_order: w.sort_order,
    })))
  } catch (e) {
    ElMessage.error('加载配置失败')
  }
})

function getItems(category) {
  return allItems.filter(d => d.category === category && !d._deleted)
}

function addItem(category, label) {
  if (!label.trim()) return
  const existing = allItems.find(d => d.category === category && d.label === label.trim() && !d._deleted)
  if (existing) { ElMessage.warning(`"${label}" 已存在`); return }
  const maxOrder = Math.max(0, ...allItems.filter(d => d.category === category && !d._deleted).map(d => d.sort_order || 0))
  allItems.push({
    id: null,
    category,
    code: `${category}_${Date.now()}`,
    label: label.trim(),
    color: '',
    sort_order: maxOrder + 1,
    is_active: true,
    _deleted: false,
    _new: true,
  })
}

function removeItem(item) {
  const idx = allItems.findIndex(d => d.id === item.id || (d.code === item.code && d.category === item.category))
  if (idx === -1) return
  
  if (allItems[idx]._new) {
    // 新增项直接移除
    allItems.splice(idx, 1)
  } else {
    // 已有项标记为删除
    allItems[idx]._deleted = true
    console.log('标记删除:', allItems[idx])
  }
}

function moveWidget(idx, dir) {
  const newIdx = idx + dir
  if (newIdx < 0 || newIdx >= widgetItems.length) return
  const tmp = widgetItems[idx]
  widgetItems[idx] = widgetItems[newIdx]
  widgetItems[newIdx] = tmp
  // 重新赋值 sort_order
  widgetItems.forEach((w, i) => { w.sort_order = i + 1 })
}

async function saveAll() {
  saving.value = true
  try {
    // 调试：打印 allItems 中的删除项
    const markedForDelete = allItems.filter(d => d._deleted)
    console.log('allItems 中标记删除的项:', markedForDelete)
    console.log('删除项的 _deleted 值:', markedForDelete.map(d => ({ id: d.id, label: d.label, _deleted: d._deleted, type: typeof d._deleted })))
    
    // 收集所有变更项（包括看板配置）
    const changedItems = [
      // 字典项
      ...allItems.filter(d => d._deleted || d._new || d.id).map(d => {
        // 使用 JSON 序列化确保响应式值被正确提取
        const raw = JSON.parse(JSON.stringify(d))
        const item = {
          id: raw.id,
          category: raw.category,
          code: raw.code,
          label: raw.label,
          sort_order: raw.sort_order,
          color: raw.color || '',
          is_active: raw.is_active,
          _deleted: raw._deleted === true
        }
        if (raw._deleted) {
          console.log('✅ 映射删除项:', { id: item.id, label: item.label, _deleted: item._deleted }, '原始:', { _deleted: raw._deleted, type: typeof raw._deleted })
        }
        return item
      }),
      // 看板配置
      ...widgetItems.map(w => ({
        id: w.id,
        category: 'dashboard_widget',
        code: w.code,
        label: w.label,
        sort_order: w.sort_order,
        color: '',
        is_active: w.is_active,
        _deleted: false
      }))
    ]
    
    // 调试：打印删除项
    const deletedItems = changedItems.filter(d => d._deleted)
    console.log('准备删除的项:', JSON.stringify(deletedItems, null, 2))
    console.log('所有发送的项:', JSON.stringify(changedItems, null, 2))
    
    // 一次请求完成所有操作
    const result = await dictApi.batchSave(changedItems)
    
    // 清理已删除项
    const toRemove = allItems.map((d, i) => d._deleted ? i : -1).filter(i => i >= 0).reverse()
    for (const i of toRemove) allItems.splice(i, 1)
    
    // 标记新增项为已保存
    for (const d of allItems.filter(d => d._new)) {
      d._new = false
    }
    
    ElMessage.success(`✅ 保存成功：新增 ${result.created}，更新 ${result.updated}，删除 ${result.deleted}`)
  } catch (e) {
    ElMessage.error('保存失败，请重试')
    console.error(e)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.config-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}
.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #2E4057;
  margin: 0 0 4px 0;
}
.page-subtitle {
  font-size: 13px;
  color: #999;
  margin: 0;
}
.config-tabs :deep(.el-tabs__header) {
  margin-bottom: 28px;
}
.config-tabs :deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 500;
}
.section-group {
  padding: 4px 0;
}

/* 看板设置列表 */
.section-title { font-size: 16px; font-weight: 600; color: #2E4057; margin: 0 0 4px 0; }
.section-desc  { font-size: 12px; color: #999; margin: 0; }
.widget-config-list { display: flex; flex-direction: column; gap: 0; }
.widget-config-row {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  border-radius: 8px;
  transition: background .15s;
  gap: 12px;
}
.widget-config-row:hover { background: #f8fafd; }
.widget-order {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e8edf8;
  color: #4472C4;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.widget-name { flex: 1; font-size: 14px; font-weight: 500; color: #303133; }
.widget-actions { display: flex; align-items: center; }
</style>
