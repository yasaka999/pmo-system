<template>
  <div class="weekly-progress-section">
    <!-- 标题栏 -->
    <div class="section-header">
      <h3 class="section-title">📅 周报进展</h3>
      <el-button type="primary" size="small" @click="openDialog()">
        <el-icon><Plus /></el-icon> 添加记录
      </el-button>
    </div>

    <!-- 进展列表 -->
    <div v-if="loading" class="loading-wrapper">
      <el-skeleton :rows="3" animated />
    </div>
    
    <div v-else-if="progressList.length === 0" class="empty-wrapper">
      <el-empty description="暂无周报进展记录" :image-size="80" />
    </div>
    
    <div v-else class="progress-list">
      <div 
        v-for="item in progressList" 
        :key="item.id" 
        class="progress-item"
      >
        <div class="progress-header">
          <div class="progress-meta">
            <span class="progress-date">{{ formatDate(item.record_date) }}</span>
            <el-tag v-if="item.progress_percent > 0" size="small" type="success">
              进度 {{ item.progress_percent }}%
            </el-tag>
            <span v-if="item.creator_name" class="progress-creator">
              记录人: {{ item.creator_name }}
            </span>
          </div>
          <div class="progress-actions">
            <el-button link type="primary" size="small" @click="openDialog(item)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(item)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
        
        <div class="progress-content">{{ item.content }}</div>
        
        <div v-if="item.next_plan" class="progress-extra">
          <div class="extra-label">下周计划:</div>
          <div class="extra-content">{{ item.next_plan }}</div>
        </div>
        
        <div v-if="item.issues" class="progress-extra">
          <div class="extra-label">遇到问题:</div>
          <div class="extra-content text-danger">{{ item.issues }}</div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑周报进展' : '添加周报进展'"
      width="600px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="记录日期" prop="record_date">
          <el-date-picker
            v-model="form.record_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="完成进度" prop="progress_percent">
          <el-slider v-model="form.progress_percent" :max="100" show-stops />
        </el-form-item>
        
        <el-form-item label="工作内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="4"
            placeholder="请描述本周工作进展..."
          />
        </el-form-item>
        
        <el-form-item label="下周计划" prop="next_plan">
          <el-input
            v-model="form.next_plan"
            type="textarea"
            :rows="2"
            placeholder="请输入下周工作计划（可选）"
          />
        </el-form-item>
        
        <el-form-item label="遇到问题" prop="issues">
          <el-input
            v-model="form.issues"
            type="textarea"
            :rows="2"
            placeholder="请输入遇到的问题（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { weeklyProgressApi } from '@/api'

const props = defineProps({
  projectId: {
    type: [String, Number],
    required: true
  }
})

// 数据状态
const loading = ref(false)
const progressList = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const currentId = ref(null)

// 表单
const formRef = ref()
const form = ref({
  record_date: new Date().toISOString().split('T')[0],
  content: '',
  progress_percent: 0,
  next_plan: '',
  issues: ''
})

const rules = {
  record_date: [{ required: true, message: '请选择记录日期', trigger: 'change' }],
  content: [{ required: true, message: '请输入工作内容', trigger: 'blur' }]
}

// 获取列表
const fetchList = async () => {
  loading.value = true
  try {
    const res = await weeklyProgressApi.list(props.projectId)
    progressList.value = res || []
  } catch (error) {
    console.error('获取周报进展失败:', error)
  } finally {
    loading.value = false
  }
}

// 打开对话框
const openDialog = (item = null) => {
  if (item) {
    // 编辑模式
    isEdit.value = true
    currentId.value = item.id
    form.value = {
      record_date: item.record_date,
      content: item.content,
      progress_percent: item.progress_percent || 0,
      next_plan: item.next_plan || '',
      issues: item.issues || ''
    }
  } else {
    // 新增模式
    isEdit.value = false
    currentId.value = null
    form.value = {
      record_date: new Date().toISOString().split('T')[0],
      content: '',
      progress_percent: 0,
      next_plan: '',
      issues: ''
    }
  }
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (isEdit.value) {
      await weeklyProgressApi.update(currentId.value, form.value)
      ElMessage.success('更新成功')
    } else {
      await weeklyProgressApi.create(props.projectId, form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchList()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    submitting.value = false
  }
}

// 删除
const handleDelete = (item) => {
  ElMessageBox.confirm(
    `确定删除 ${formatDate(item.record_date)} 的周报进展记录吗？`,
    '确认删除',
    { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
    await weeklyProgressApi.remove(item.id)
    ElMessage.success('删除成功')
    fetchList()
  }).catch(() => {})
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.weekly-progress-section {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.section-title {
  margin: 0;
  font-size: 16px;
  color: #2E4057;
}

.loading-wrapper {
  padding: 20px;
}

.empty-wrapper {
  padding: 40px 0;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-item {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 12px 16px;
  border-left: 4px solid #409eff;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-date {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.progress-creator {
  font-size: 12px;
  color: #909399;
}

.progress-actions {
  display: flex;
  gap: 4px;
}

.progress-content {
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
  margin-bottom: 8px;
}

.progress-extra {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #dcdfe6;
  display: flex;
  gap: 8px;
}

.extra-label {
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
  font-weight: 500;
}

.extra-content {
  font-size: 13px;
  color: #606266;
  flex: 1;
}

.text-danger {
  color: #f56c6c;
}
</style>
