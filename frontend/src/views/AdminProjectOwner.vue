<template>
  <div class="project-owner-config">
    <h2>项目负责人分配</h2>
    <p class="desc">仅管理员和 PMO 可以重新分配项目负责人</p>
    
    <!-- 项目列表表格 -->
    <el-table :data="projects" border v-loading="loading" stripe>
      <el-table-column prop="code" label="项目编号" width="120" />
      <el-table-column prop="name" label="项目名称" min-width="200" show-overflow-tooltip />
      <el-table-column prop="owner_name" label="当前负责人" width="120">
        <template #default="{ row }">
          <span v-if="row.owner_name">{{ row.owner_name }}</span>
          <el-tag v-else size="small" type="info">无负责人</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button 
            type="primary" 
            size="small"
            @click="openReassignDialog(row)"
          >
            重新分配
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 重新分配对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      title="重新分配负责人"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="项目编号">
          <el-input :value="currentProject.code" disabled />
        </el-form-item>
        <el-form-item label="项目名称">
          <el-input :value="currentProject.name" disabled />
        </el-form-item>
        <el-form-item label="当前负责人">
          <el-input :value="currentProject.owner_name || '无'" disabled />
        </el-form-item>
        <el-form-item label="新负责人" required>
          <el-select 
            v-model="form.newOwnerId" 
            placeholder="选择新负责人"
            filterable
            style="width: 100%"
          >
            <el-option 
              v-for="user in users" 
              :key="user.id"
              :label="`${user.username} (${user.full_name || '无'}) - ${user.role}`"
              :value="user.id"
            >
              <span style="float: left">{{ user.username }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                {{ user.full_name || '无' }} - {{ user.role }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmReassign" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api'

const loading = ref(false)
const submitting = ref(false)
const projects = ref([])
const users = ref([])
const dialogVisible = ref(false)
const currentProject = ref({})
const form = reactive({
  newOwnerId: null
})

// 加载项目列表
const loadProjects = async () => {
  loading.value = true
  try {
    projects.value = await adminApi.getProjectOwners()
  } catch (error) {
    ElMessage.error('加载项目列表失败')
  } finally {
    loading.value = false
  }
}

// 加载用户列表
const loadUsers = async () => {
  try {
    users.value = await adminApi.getUsers()
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  }
}

// 打开重新分配对话框
const openReassignDialog = (project) => {
  currentProject.value = project
  form.newOwnerId = null
  dialogVisible.value = true
}

// 确认重新分配
const confirmReassign = async () => {
  if (!form.newOwnerId) {
    ElMessage.warning('请选择新负责人')
    return
  }
  
  submitting.value = true
  try {
    const result = await adminApi.reassignOwner(currentProject.value.id, form.newOwnerId)
    ElMessage.success(`负责人已更新为 ${result.new_owner_name}`)
    dialogVisible.value = false
    loadProjects() // 刷新列表
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadProjects()
  loadUsers()
})
</script>

<style scoped>
.project-owner-config {
  padding: 20px;
}

h2 {
  margin-bottom: 10px;
  color: #303133;
}

.desc {
  color: #909399;
  margin-bottom: 20px;
  font-size: 14px;
}
</style>
