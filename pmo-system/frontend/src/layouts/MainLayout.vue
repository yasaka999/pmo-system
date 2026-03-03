<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="collapsed ? '64px' : '220px'" class="sidebar">
      <div class="sidebar-logo">
        <el-icon class="logo-icon"><DataBoard /></el-icon>
        <span v-if="!collapsed" class="logo-text">PMO系统</span>
      </div>

      <el-menu
        :default-active="$route.path"
        :collapse="collapsed"
        router
        background-color="#1a2840"
        text-color="#c0cfe4"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <template #title>项目总览</template>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><FolderOpened /></el-icon>
          <template #title>项目列表</template>
        </el-menu-item>

        <el-divider v-if="currentProjectId && !collapsed" style="border-color:#2d3e58;margin:8px 0"/>
        <template v-if="currentProjectId">
          <div v-if="!collapsed" class="sidebar-section">当前项目</div>
          <el-menu-item :index="`/projects/${currentProjectId}`">
            <el-icon><InfoFilled /></el-icon>
            <template #title>项目详情</template>
          </el-menu-item>
          <el-menu-item :index="`/projects/${currentProjectId}/milestones`">
            <el-icon><Calendar /></el-icon>
            <template #title>里程碑进度</template>
          </el-menu-item>
          <el-menu-item :index="`/projects/${currentProjectId}/issues`">
            <el-icon><Warning /></el-icon>
            <template #title>问题台账</template>
          </el-menu-item>
          <el-menu-item :index="`/projects/${currentProjectId}/risks`">
            <el-icon><Bell /></el-icon>
            <template #title>风险台账</template>
          </el-menu-item>
          <el-menu-item :index="`/projects/${currentProjectId}/mandays`">
            <el-icon><Timer /></el-icon>
            <template #title>人天管理</template>
          </el-menu-item>
          <el-menu-item :index="`/projects/${currentProjectId}/reports`">
            <el-icon><Document /></el-icon>
            <template #title>报告生成</template>
          </el-menu-item>
        </template>
        
        <template v-if="auth.user?.role === 'admin'">
          <el-divider v-if="!collapsed" style="border-color:#2d3e58;margin:8px 0"/>
          <div v-if="!collapsed" class="sidebar-section">系统管理</div>
          <el-menu-item index="/system/users">
            <el-icon><UserFilled /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          <el-menu-item index="/system/config">
            <el-icon><Setting /></el-icon>
            <template #title>系统配置</template>
          </el-menu-item>
        </template>
      </el-menu>

      <div class="sidebar-footer">
        <el-icon class="collapse-btn" @click="collapsed = !collapsed">
          <Fold v-if="!collapsed" /><Expand v-else />
        </el-icon>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶栏 -->
      <el-header class="topbar">
        <div class="topbar-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="$route.meta.title">{{ $route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="topbar-right">
          <el-dropdown @command="handleCmd">
            <div class="user-info">
              <el-avatar :size="32" style="background:#4472C4">{{ userInitial }}</el-avatar>
              <span class="username">{{ auth.user?.full_name || auth.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 页面内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 修改密码弹窗 -->
    <el-dialog title="修改个人密码" v-model="pwdDialog.visible" width="400px">
      <el-form :model="pwdDialog.form" :rules="pwdRules" ref="pwdFormRef" label-width="90px">
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="pwdDialog.form.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdDialog.form.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="pwdDialog.form.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submitPwd" :loading="pwdDialog.loading">提交</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { userApi } from '@/api'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const route = useRoute()
const collapsed = ref(false)

const currentProjectId = computed(() => route.params.id || null)
const userInitial = computed(() => {
  const name = auth.user?.full_name || auth.user?.username || 'U'
  return name.charAt(0).toUpperCase()
})

const pwdFormRef = ref(null)
const pwdDialog = reactive({
  visible: false,
  loading: false,
  form: { old_password: '', new_password: '', confirm_password: '' }
})

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== pwdDialog.form.new_password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
  confirm_password: [{ required: true, validator: validatePass2, trigger: 'blur' }]
}

function handleCmd(cmd) {
  if (cmd === 'logout') {
    auth.logout()
  } else if (cmd === 'password') {
    pwdDialog.form = { old_password: '', new_password: '', confirm_password: '' }
    pwdDialog.visible = true
  }
}

async function submitPwd() {
  if (!pwdFormRef.value) return
  await pwdFormRef.value.validate(async (valid) => {
    if (valid) {
      pwdDialog.loading = true
      try {
        await userApi.changePassword({
          old_password: pwdDialog.form.old_password,
          new_password: pwdDialog.form.new_password
        })
        ElMessage.success('密码修改成功，请重新登录')
        pwdDialog.visible = false
        auth.logout() // 强制重新登录
      } finally {
        pwdDialog.loading = false
      }
    }
  })
}
</script>

<style scoped>
.layout-container { height: 100vh; overflow: hidden; }

.sidebar {
  background: #1a2840;
  display: flex;
  flex-direction: column;
  transition: width 0.2s;
  overflow: hidden;
}

.sidebar-logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 10px;
  border-bottom: 1px solid #2d3e58;
}
.logo-icon { font-size: 24px; color: #4472C4; }
.logo-text { font-size: 17px; font-weight: 700; color: #fff; white-space: nowrap; }

.sidebar-section {
  padding: 4px 20px;
  font-size: 11px;
  color: #5d7a99;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.el-menu { border-right: none; flex: 1; }

.sidebar-footer {
  padding: 12px 20px;
  border-top: 1px solid #2d3e58;
  display: flex;
  justify-content: flex-end;
}
.collapse-btn { color: #c0cfe4; font-size: 18px; cursor: pointer; }

.topbar {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e8edf3;
  padding: 0 24px;
  height: 56px;
}
.topbar-right { display: flex; align-items: center; }
.user-info { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.username { font-size: 14px; color: #333; }

.main-content {
  background: #F0F2F5;
  padding: 20px;
  overflow-y: auto;
}
</style>
