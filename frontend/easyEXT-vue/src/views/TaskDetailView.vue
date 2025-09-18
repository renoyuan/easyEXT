<script setup lang="ts">
// 任务详情页
import { defineComponent, ref, onMounted, computed,reactive } from 'vue';
import { useRoute } from 'vue-router'
import { fetchDetail } from '@/api/api'
import type { ElMessage,FormInstance, FormRules } from 'element-plus'


const route = useRoute()
const taskId = route.query.taskId as string


const taskDetail = ref({})

// 动态表单字段配置（从后端获取）
const formFields = ref<any[]>([]);
    
// 表单数据对象（响应式）
const formData = ref<any[]>([]); // 表单验证规则（根据字段配置动态生成）

// 表单验证规则（根据字段配置动态生成）
const dynamicFormRef = ref<FormInstance | null>(null);
const activeNames = ref<any[]>([]);
onMounted(async () => {
  console.log('下游任务ID:', taskId)
  taskDetail.value  = await fetchDetail(taskId)
  
  console.log('任务详情',taskDetail.value)
  formFields.value = taskDetail.value.data.element_config || []
  formData.value = taskDetail.value.data.task_info || {}
  console.log('表单结果',formData.value)
  console.log('表单字段配置:', formFields.value)
})

// 假设后端返回的字段配置格式
interface FormField {
  type: 'input' | 'select' | 'number'; // 字段类型
  label: string; // 标签名
  prop: string; // 表单绑定的字段名
  rules?: Array<{ required: boolean; message: string }>; // 验证规则
  options?: Array<{ label: string; value: string }>; // 下拉选项（select 专用）
} 



// 表单验证规则（动态生成）
    const formRules = computed(() => {
      const rules: Record<string, any[]> = {};
      formFields.value.forEach(field => {
        if (field.rules) {
          rules[field.prop] = field.rules;
        }
      });
      return rules;
    });



    // 根据类型返回组件
    const getComponentType = (type: string) => {
      const componentMap: Record<string, string> = {
        input: 'el-input',
        select: 'el-select',
        number: 'el-input-number'
      };
      return componentMap[type] || 'el-input';
    };
    // 获取组件属性
    const getFieldProps = (field: FormField) => {
      const props: Record<string, any> = {
        placeholder: `请输入${field.label}`
      };
      
      // 处理下拉选项
      if (field.type === 'select' && field.options) {
        props.options = field.options.map(option => ({
          label: option.label,
          value: option.value
        }));
      }
      
      return props;
    };

  // 提交表单
  const handleSubmit = () => {
    
      console.log('提交数据:', formData.value);
      // 发送至后端
      }




</script>

<template>
  <el-scrollbar height="1050px" >
  <el-form :model="formData" label-width="120px" :rules="formRules">
    <!-- 修正折叠面板结构 -->
    <el-collapse v-model="activeNames">
      <el-collapse-item 
        v-for="(group, index) in formData" 
        :key="index" 
        :title="` ${index}`" 
        :name="index"
      >
        <!-- 动态渲染表单项 -->
        <el-form-item 
          v-for="(field, fieldIndex) in formFields" 
          :key="fieldIndex" 
          :label="field" 
          :prop="`groups[${index}].${field}`" 
        >
          <el-input v-model="formData[index][field]" />
        </el-form-item>
      </el-collapse-item>
    </el-collapse>
  </el-form>
  </el-scrollbar>
</template>

<style scoped>
</style>
        
  