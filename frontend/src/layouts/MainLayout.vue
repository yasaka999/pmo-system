<template>
  <el-container class="layout-container">

    <!-- ══ PC 侧边栏（手机端隐藏） ══ -->
    <el-aside :width="collapsed ? '64px' : '220px'" class="sidebar hide-mobile">
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
        <el-menu-item v-if="auth.user && ['admin','pmo'].includes(auth.user.role)" index="/portfolio-report">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>整体报告</template>
        </el-menu-item>

        <template v-if="currentProjectId">
          <el-divider v-if="!collapsed" style="border-color:#2d3e58;margin:8px 0"/>
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

          <el-menu-item index="/operation-logs">
            <el-icon><Document /></el-icon>
            <template #title>操作日志</template>
          </el-menu-item>

        <template v-if="auth.user && ['admin', 'pmo'].includes(auth.user.role)">
          <el-divider v-if="!collapsed" style="border-color:#2d3e58;margin:8px 0"/>
          <div v-if="!collapsed" class="sidebar-section">系统管理</div>
          <el-menu-item index="/system/users" v-if="auth.user && auth.user.role === 'admin'">
            <el-icon><UserFilled /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/project-owners" v-if="auth.user && ['admin', 'pmo'].includes(auth.user.role)"><el-icon><User /></el-icon><template #title>项目负责人分配</template></el-menu-item>
          <el-menu-item index="/system/config" v-if="auth.user && ['admin', 'pmo'].includes(auth.user.role)"><el-icon><Setting /></el-icon><template #title>系统配置</template></el-menu-item></template>
      </el-menu>

      <div class="sidebar-footer">
        <el-icon class="collapse-btn" @click="collapsed = !collapsed">
          <Fold v-if="!collapsed" /><Expand v-else />
        </el-icon>
      </div>
    </el-aside>

    <!-- ══ 主内容区 ══ -->
    <el-container>
      <!-- 顶栏 -->
      <el-header class="topbar">
        <!-- 手机端汉堡按钮 -->
        <el-icon class="hamburger show-mobile" @click="drawerVisible = true">
          <Expand />
        </el-icon>
        <!-- PC 端面包屑 -->
        <div class="topbar-left hide-mobile">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="$route.meta.title">{{ $route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <!-- 手机端页面标题 -->
        <div class="mobile-page-title show-mobile">{{ $route.meta.title || 'PMO系统' }}</div>

        <div class="topbar-right">
          <el-dropdown @command="handleCmd">
            <div class="user-info">
              <el-avatar :size="32" style="background:#4472C4">{{ userInitial }}</el-avatar>
              <span class="username hide-mobile">{{ auth.user?.full_name || auth.user?.username }}</span>
              <el-icon class="hide-mobile"><ArrowDown /></el-icon>
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

    <!-- ══ 手机端导航 Drawer ══ -->
    <el-drawer
      v-model="drawerVisible"
      direction="ltr"
      :size="240"
      :with-header="false"
      class="mobile-nav-drawer"
    >
      <div class="sidebar-logo" style="background:#1a2840;padding:0 20px;height:60px;display:flex;align-items:center;gap:10px;">
        <el-icon style="font-size:24px;color:#4472C4"><DataBoard /></el-icon>
        <span style="font-size:17px;font-weight:700;color:#fff;">PMO系统</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#1a2840"
        text-color="#c0cfe4"
        active-text-color="#ffffff"
        @select="drawerVisible = false"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <template #title>项目总览</template>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><FolderOpened /></el-icon>
          <template #title>项目列表</template>
        </el-menu-item>
        <el-menu-item v-if="auth.user && ['admin','pmo'].includes(auth.user.role)" index="/portfolio-report">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>整体报告</template>
        </el-menu-item>

        <template v-if="currentProjectId">
          <el-divider style="border-color:#2d3e58;margin:8px 0"/>
          <div class="sidebar-section">当前项目</div>
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

          <el-menu-item index="/operation-logs">
            <el-icon><Document /></el-icon>
            <template #title>操作日志</template>
          </el-menu-item>

        <template v-if="auth.user && ['admin', 'pmo'].includes(auth.user.role)">
          <el-divider style="border-color:#2d3e58;margin:8px 0"/>
          <div class="sidebar-section">系统管理</div>
          <el-menu-item index="/system/users" v-if="auth.user && auth.user.role === 'admin'">
            <el-icon><UserFilled /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/project-owners" v-if="auth.user && ['admin', 'pmo'].includes(auth.user.role)"><el-icon><User /></el-icon><template #title>项目负责人分配</template></el-menu-item>
          <el-menu-item index="/system/config" v-if="auth.user && ['admin', 'pmo'].includes(auth.user.role)"><el-icon><Setting /></el-icon><template #title>系统配置</template></el-menu-item></template>
      </el-menu>

      <!-- 用户信息 & 退出 -->
      <div class="mobile-nav-footer">
        <el-avatar :size="36" style="background:#4472C4">{{ userInitial }}</el-avatar>
        <div class="mobile-nav-user">
          <div style="font-size:13px;font-weight:600;color:#fff;">{{ auth.user?.full_name || auth.user?.username }}</div>
          <div style="font-size:11px;color:#5d7a99;">{{ auth.user?.role }}</div>
        </div>
        <el-icon style="color:#c0cfe4;cursor:pointer;margin-left:auto;" @click="handleCmd('logout')"><SwitchButton /></el-icon>
      </div>
    </el-drawer>

    <!-- 修改密码弹窗 -->
    <el-dialog title="修改个人密码" v-model="pwdDialog.visible" width="min(400px, 92vw)">
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
const drawerVisible = ref(false)   // 手机端导航 Drawer

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
        auth.logout()
      } finally {
        pwdDialog.loading = false
      }
    }
  })
}
</script>

<style scoped>
.layout-container { height: 100vh; overflow: hidden; }

/* ── PC 侧边栏 ── */
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

.el-menu { border-right: none; flex: 1; overflow-y: auto; }

.sidebar-footer {
  padding: 12px 20px;
  border-top: 1px solid #2d3e58;
  display: flex;
  justify-content: flex-end;
}
.collapse-btn { color: #c0cfe4; font-size: 18px; cursor: pointer; }

/* ── 顶栏 ── */
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

/* 汉堡按钮（手机端） */
.hamburger {
  font-size: 22px;
  color: #2E4057;
  cursor: pointer;
  padding: 4px;
}
.mobile-page-title {
  font-size: 15px;
  font-weight: 600;
  color: #2E4057;
  flex: 1;
  text-align: center;
  margin: 0 8px;
}

/* ── 主内容区 ── */
.main-content {
  background: #F0F2F5;
  padding: 20px;
  overflow-y: auto;
}
@media (max-width: 768px) {
  .main-content { padding: 12px; }
  .topbar { padding: 0 12px; }
}

/* ── 手机端导航 Drawer ── */
.mobile-nav-drawer :deep(.el-drawer__body) {
  padding: 0;
  background: #1a2840;
  display: flex;
  flex-direction: column;
}
.mobile-nav-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid #2d3e58;
  margin-top: auto;
}
</style>
