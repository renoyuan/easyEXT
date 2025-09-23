<script setup lang="ts">
import { ref, computed, defineExpose } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Image as ImageIcon } from '@element-plus/icons-vue'
import { UploadFile } from 'element-plus'
import { ElUpload } from 'element-plus'
import {uploadTask} from '@/api/api'

// 确保定义了所有 props，并且类型正确
const props = defineProps({
  sceneID: {
    type: Number, // 注意类型是 Number，因为父组件使用了 Number(item.id)
    required: true // 如果该 prop 是必需的，请设置
  },
  sceneName: {
    type: String,
    required: true
  },
  visible: {
    type: Boolean,
    required: true
  }
})

// 组件属性
const propsa = ({

  allowedTypes: {
    type: String,
    default: '.jpg,.jpeg,.png,.pdf'
  },
  maxSizeMB: {
    type: Number,
    default: 5
  }
})



// 新增响应式数据
const fileInputRef = ref<HTMLInputElement | null>(null)
const selectedFiles = ref<File[]>([])

// 修改原有方法：处理文件选择
const handleFileSelect = (event: Event) => {
const files = (event.target as HTMLInputElement).files
  if (files) {
    selectedFiles.value = Array.from(files)
  }
}

// 新增方法：触发文件选择
const triggerFileSelect = () => {
  fileInputRef.value?.click()
}

// 类型定义
interface FileItem {
  name: string
  size: number
  type: string
  url: string
}



// 响应式数据
const dialogVisible = ref(false)
const previewVisible = ref(false)
const previewUrl = ref('')
const fileList = ref<FileItem[]>([])
const uploadRef = ref<InstanceType<typeof ElUpload> | null>(null)


// 计算属性
const allowedTypesText = computed(() => {
  return propsa.allowedTypes
    .split(',')
    .map(t => t.replace(/^\./, ''))
    .join('/ ')
})

// 方法
const openUploadDialog = () => {
  dialogVisible.value = true
}

const handleClose = () => {
  fileList.value = []
  previewVisible.value = false
}

const beforeUpload = (file: File) => {
  const isTypeValid = propsa.allowedTypes.includes(`.${file.name.split('.').pop()}`)
  const isLtMaxSize = file.size <= propsa.maxSizeMB * 1024 * 1024

  if (!isTypeValid) {
    ElMessage.error(`不支持的文件类型：${file.name}`)
  }
  if (!isLtMaxSize) {
    ElMessage.error(`文件大小不能超过 ${propsa.maxSizeMB}MB`)
  }

  return isTypeValid && isLtMaxSize
}

const handleChange = (file: UploadFile) => {
  if (file.status === 'ready') {
    fileList.value = fileList.value.map(item => ({
      ...item,
      url: URL.createObjectURL(file.raw)
    }))
  }
}

const handleSuccess = (response: any, file: UploadFile) => {
  ElMessage.success('上传成功')
  fileList.value = fileList.value.map(item => ({
    ...item,
    url: response.url
  }))
}

const handleError = (err: any, file: UploadFile) => {
  ElMessage.error(`上传失败：${err.message}`)
}

async function submitUpload() {
  if (selectedFiles.value.length === 0) return
  for (const file of selectedFiles.value) {
    try {
      const res = await uploadTask({
        file,
        sceneID: props.sceneID
      })
      console.log('上传成功', res.data)
    } catch (e) {
      console.error('上传失败', e)
    }
  }
}

const previewImage = (url: string) => {
  previewUrl.value = url
  previewVisible.value = true
}

// 暴露子组件方法
defineExpose({
  openUploadDialog
})
</script>

<template>
  <!-- 触发按钮 -->
  <el-button type="primary" @click="openUploadDialog">
    <i-ep-plus class="mr-2" /> 上传文件
  </el-button>

  <!-- 上传弹窗 -->
  <el-dialog
    v-model="dialogVisible"
    :before-close="handleClose"
    :title="`${props.sceneName || '未知场景'} - 文件上传`"
    width="900px"
    
  >
    <!-- 上传区域 -->
    <template #content>
      <el-upload
        ref="uploadRef"
       
        :before-upload="beforeUpload"
        :on-change="handleChange"
        :on-success="handleSuccess"
        :on-error="handleError"
        :file-list="fileList"
        :limit="5"
        :accept="allowedTypes"
        list-type="picture-card"
      >
        <i-ep-plus class="upload-icon" />
        <div class="el-upload__tip">
          支持 {{ allowedTypesText }}，单文件不超过 {{ maxSizeMB }}MB
        </div>
      </el-upload>
    </template>

    <!-- 预览区域 -->
    <template #preview>
      <div v-if="previewVisible" class="preview-container">
        <img :src="previewUrl" class="preview-image" />
        <el-button @click="previewVisible = false">关闭预览</el-button>
      </div>
    </template>

    <!-- 操作按钮 -->
   
    <template #footer>
      <el-button type="primary" @click="triggerFileSelect">
        <i-ep-plus class="mr-2" /> 选择文件
      </el-button>
        <!-- 隐藏的文件输入框 -->
        <input 
          type="file" 
          ref="fileInputRef" 
          style="display: none"
          :accept="allowedTypes"
          @change="handleFileSelect"
          multiple
        />
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitUpload">确认上传</el-button>
    </template>
  </el-dialog>
</template>



<style scoped>
.upload-icon {
  font-size: 48px;
  color: #C0C4CC;
  transition: all 0.3s;
}

.preview-container {
  max-width: 80%;
  max-height: 80vh;
  margin: 20px auto;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: auto;
  border-radius: 8px;
}

.el-upload__tip {
  margin-top: 10px;
  color: #606266;
  font-size: 12px;
}
</style>