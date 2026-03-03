<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">里程碑与进度管理</h2>
      <el-button type="primary" @click="openMsDialog()"><el-icon><Plus /></el-icon> 添加里程碑</el-button>
    </div>

    <div v-for="ms in milestones" :key="ms.id" class="page-card" style="margin-bottom:12px">
      <div class="ms-header">
        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;flex:1">
          <el-tag :type="msTagType(ms.status)" size="small">{{ ms.status }}</el-tag>
          <span style="font-weight:600;font-size:16px">{{ ms.name }}</span>
          <span style="color:#999;font-size:12px">计划: {{ ms.plan_date || '-' }}  实际: {{ ms.actual_date || '-' }}</span>
        </div>
        <div style="display:flex;gap:6px;flex-shrink:0;margin-top:4px">
          <el-button size="small" @click="openTaskDialog(ms.id)"><el-icon><Plus /></el-icon> 添加任务</el-button>
          <el-button size="small" type="warning" @click="openMsDialog(ms)">编辑</el-button>
          <el-popconfirm title="删除里程碑会同时删除其下所有任务，确认？" @confirm="deleteMilestone(ms.id)">
            <template #reference><el-button size="small" type="danger">删除</el-button></template>
          </el-popconfirm>
        </div>
      </div>

      <!-- PC 任务表格 -->
      <el-table :data="tasksByMs(ms.id)" size="small" style="width:100%;margin-top:10px" class="hide-mobile">
        <el-table-column prop="name" label="工作项" min-width="200" />
        <el-table-column prop="assignee" label="负责人" width="100" />
        <el-table-column prop="plan_start" label="计划开始" width="110" />
        <el-table-column prop="plan_end" label="计划结束" width="110" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="msTagType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="完成度" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :stroke-width="8" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" align="center">
          <template #default="{ row }">
            <el-button size="small" type="warning" @click="openTaskDialog(ms.id, row)">编辑</el-button>
            <el-popconfirm title="确认删除？" @confirm="deleteTask(row.id)">
              <template #reference><el-button size="small" type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 手机端任务卡片 -->
      <div class="show-mobile" style="margin-top:10px">
        <div class="mobile-card-list">
          <div class="m-card" v-for="task in tasksByMs(ms.id)" :key="task.id">
            <div class="m-card-header">
              <div class="m-card-title">{{ task.name }}</div>
              <el-tag :type="msTagType(task.status)" size="small">{{ task.status }}</el-tag>
            </div>
            <div class="m-card-body">
              <div class="m-field"><span class="m-field-label">负责人</span><span class="m-field-value">{{ task.assignee || '-' }}</span></div>
              <div class="m-field"><span class="m-field-label">完成度</span>
                <el-progress :percentage="task.progress" :stroke-width="6" style="width:80px" />
              </div>
              <div class="m-field"><span class="m-field-label">计划结束</span><span class="m-field-value">{{ task.plan_end || '-' }}</span></div>
            </div>
            <div class="m-card-footer">
              <el-button size="small" type="warning" @click="openTaskDialog(ms.id, task)">编辑</el-button>
              <el-popconfirm title="确认删除？" @confirm="deleteTask(task.id)">
                <template #reference><el-button size="small" type="danger">删除</el-button></template>
              </el-popconfirm>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 里程碑对话框 -->
    <el-dialog v-model="msDlg" :title="editMsId ? '编辑里程碑' : '新建里程碑'" width="min(480px, 95vw)">
      <el-form :model="msForm" label-width="90px">
        <el-form-item label="名称"><el-input v-model="msForm.name" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="msForm.status" style="width:100%">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划日期"><el-date-picker v-model="msForm.plan_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="实际日期"><el-date-picker v-model="msForm.actual_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="msForm.order_index" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="msForm.description" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="msDlg = false">取消</el-button>
        <el-button type="primary" @click="saveMilestone">保存</el-button>
      </template>
    </el-dialog>

    <!-- 任务对话框 -->
    <el-dialog v-model="taskDlg" :title="editTaskId ? '编辑任务' : '新建任务'" width="min(560px, 95vw)">
      <el-form :model="taskForm" label-width="90px">
        <el-form-item label="任务名称"><el-input v-model="taskForm.name" /></el-form-item>
        <el-form-item label="负责人"><el-input v-model="taskForm.assignee" /></el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="计划开始"><el-date-picker v-model="taskForm.plan_start" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计划结束"><el-date-picker v-model="taskForm.plan_end" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-select v-model="taskForm.status" style="width:100%">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="完成度(%)"><el-slider v-model="taskForm.progress" :step="5" show-input /></el-form-item>
        <el-form-item label="备注"><el-input v-model="taskForm.notes" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskDlg = false">取消</el-button>
        <el-button type="primary" @click="saveTask">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { milestoneApi, taskApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useDictStore } from '@/stores/dict'

const dictStore = useDictStore()
const route = useRoute()
const pid = route.params.id

const milestones = ref([])
const tasks = ref([])
const msDlg = ref(false)
const taskDlg = ref(false)
const editMsId = ref(null)
const editTaskId = ref(null)
const currentMsId = ref(null)

const statusOptions = computed(() => dictStore.getOptions('milestone_status'))

const msForm = ref({ name:'', status:'未开始', plan_date:null, actual_date:null, description:'', order_index:0 })
const taskForm = ref({ name:'', assignee:'', plan_start:null, plan_end:null, status:'未开始', progress:0, notes:'' })

async function load() {
  milestones.value = await milestoneApi.list(pid)
  tasks.value = await taskApi.list(pid)
}

function tasksByMs(msId) { return tasks.value.filter(t => t.milestone_id === msId) }

function msTagType(s) {
  const c = dictStore.getDictItem('milestone_status', s).color
  return c || { '已完成': 'success', '进行中': 'primary', '延期': 'danger', '未开始': 'info' }[s] || ''
}

function openMsDialog(ms = null) {
  editMsId.value = ms?.id || null
  msForm.value = ms ? { ...ms } : { name:'', status:'未开始', plan_date:null, actual_date:null, description:'', order_index:0 }
  msDlg.value = true
}

async function saveMilestone() {
  if (!msForm.value.name) { ElMessage.warning('里程碑名称必填'); return }
  if (editMsId.value) await milestoneApi.update(editMsId.value, msForm.value)
  else await milestoneApi.create(pid, { ...msForm.value, project_id: Number(pid) })
  ElMessage.success('保存成功'); msDlg.value = false; await load()
}

async function deleteMilestone(id) {
  await milestoneApi.remove(id); ElMessage.success('已删除'); await load()
}

function openTaskDialog(msId, task = null) {
  currentMsId.value = msId
  editTaskId.value = task?.id || null
  taskForm.value = task ? { ...task } : { name:'', assignee:'', plan_start:null, plan_end:null, status:'未开始', progress:0, notes:'' }
  taskDlg.value = true
}

async function saveTask() {
  if (!taskForm.value.name) { ElMessage.warning('任务名称必填'); return }
  const data = { ...taskForm.value, milestone_id: currentMsId.value, project_id: Number(pid) }
  if (editTaskId.value) await taskApi.update(editTaskId.value, data)
  else await taskApi.create(pid, data)
  ElMessage.success('保存成功'); taskDlg.value = false; await load()
}

async function deleteTask(id) {
  await taskApi.remove(id); ElMessage.success('已删除'); await load()
}

onMounted(() => {
  dictStore.fetchDicts()
  load()
})
</script>

<style scoped>
.page-title { font-size: 20px; font-weight: 600; color: #2E4057; }
.ms-header { display: flex; align-items: center; justify-content: space-between; }
</style>
