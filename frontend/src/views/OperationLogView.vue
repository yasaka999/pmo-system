<template>
  <div class="operation-log-view">
    <h2>操作日志</h2>
    
    <!-- 筛选条件 -->
    <div class="filters" v-if="auth.user?.role === 'admin'">
      <el-select 
        v-model="filters.user_id" 
        placeholder="选择用户" 
        clearable
        @change="fetchLogs"
        style="width: 200px"
      >
        <el-option
          v-for="user in users"
          :key="user.user_id"
          :label="user.username"
          :value="user.user_id"
        />
      </el-select>
      
      <el-button type="primary" @click="fetchLogs" :loading="loading">查询</el-button>
    </div>
    
    <!-- 日志表格 -->
    <el-table :data="logs" border v-loading="loading" stripe style="margin-top: 20px">
      <el-table-column prop="username" label="操作用户" width="120" />
      <el-table-column prop="action" label="操作类型" width="100">
        <template #default="{ row }">
          <el-tag :type="getActionType(row.action)">{{ row.action }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="module" label="模块" width="120" />
      <el-table-column prop="description" label="操作描述" min-width="250" show-overflow-tooltip />
      <el-table-column prop="request_method" label="请求方法" width="100">
        <template #default="{ row }">
          <el-tag :type="getMethodType(row.request_method)" size="small">{{ row.request_method }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="ip_address" label="IP 地址" width="140" />
      <el-table-column prop="created_at" label="操作时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.size"
      :total="pagination.total"
      :page-sizes="[20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @current-change="fetchLogs"
      @size-change="fetchLogs"
      style="margin-top: 20px; justify-content: flex-end"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { operationLogsApi } from '@/api'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const loading = ref(false)
const logs = ref([])
const users = ref([])

const filters = reactive({
  user_id: null
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const fetchLogs = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size
    }
    
    // admin 可以筛选用户
    if (auth.user?.role === 'admin' && filters.user_id) {
      params.user_id = filters.user_id
    }
    
    const resp = await operationLogsApi.list(params)
    logs.value = resp
    pagination.total = resp.length // 简化处理，实际应该从后端获取总数
  } catch (error) {
    ElMessage.error('加载日志失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const fetchUsers = async () => {
  if (auth.user?.role !== 'admin') return
  
  try {
    const resp = await operationLogsApi.users()
    users.value = resp
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

const getActionType = (action) => {
  const typeMap = {
    'CREATE': 'success',
    'UPDATE': 'warning',
    'DELETE': 'danger',
    'LOGIN': 'info',
    'LOGOUT': 'info'
  }
  return typeMap[action] || 'info'
}

const getMethodType = (method) => {
  const typeMap = {
    'POST': 'success',
    'PUT': 'warning',
    'DELETE': 'danger',
    'GET': 'info'
  }
  return typeMap[method] || 'info'
}

const formatTime = (time) => {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  fetchLogs()
  fetchUsers()
})
</script>

<style scoped>
.operation-log-view {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  color: #303133;
}

.filters {
  display: flex;
  gap: 10px;
  align-items: center;
}
</style>
