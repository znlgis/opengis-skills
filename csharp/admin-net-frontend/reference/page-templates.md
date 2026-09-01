# Admin.NET Frontend Page Templates Reference

Page templates, common components, styles and themes split from SKILL.md.

---

## 页面开发模板

### 标准 CRUD 页面

```vue
<template>
  <div class="my-page-container">
    <!-- 搜索区域 -->
    <el-card shadow="hover">
      <el-form :model="queryParams" :inline="true">
        <el-form-item label="名称">
          <el-input v-model="queryParams.name" placeholder="请输入名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">
            <el-icon><ele-Search /></el-icon> 查询
          </el-button>
          <el-button @click="resetQuery">
            <el-icon><ele-Refresh /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作按钮 -->
    <el-card shadow="hover" style="margin-top: 8px">
      <el-button v-auth="'myBiz:add'" type="primary" @click="openAddDialog">
        <el-icon><ele-Plus /></el-icon> 新增
      </el-button>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="remark" label="备注" />
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button v-auth="'myBiz:edit'" type="warning" size="small"
              @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button v-auth="'myBiz:delete'" type="danger" size="small"
              @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:currentPage="queryParams.page"
        v-model:page-size="queryParams.pageSize"
        :total="total"
        @current-change="handleQuery"
        @size-change="handleQuery"
        layout="total, sizes, prev, pager, next, jumper"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import { getAPI } from '/@/utils/axios-utils';
import { MyBizApi } from '/@/api-services/api';

const loading = ref(false);
const tableData = ref([]);
const total = ref(0);
const queryParams = ref({
    name: '',
    page: 1,
    pageSize: 20,
});

const handleQuery = async () => {
    loading.value = true;
    const res = await getAPI(MyBizApi).apiMyBizPagePost(queryParams.value);
    tableData.value = res.data.result?.items ?? [];
    total.value = res.data.result?.total ?? 0;
    loading.value = false;
};

const resetQuery = () => {
    queryParams.value = { name: '', page: 1, pageSize: 20 };
    handleQuery();
};

const handleDelete = (row: any) => {
    ElMessageBox.confirm('确定删除吗？', '提示', { type: 'warning' }).then(async () => {
        await getAPI(MyBizApi).apiMyBizDeletePost({ id: row.id });
        ElMessage.success('删除成功');
        handleQuery();
    });
};

onMounted(() => {
    handleQuery();
});
</script>
```

---

## 常用组件

| 组件 | 包 / 路径 | 用途 |
|------|----------|------|
| `el-table` / `el-form` / `el-dialog` | Element Plus | 表格、表单、对话框 |
| `el-tree` / `el-tree-select` | Element Plus | 树形选择（机构、菜单） |
| `el-upload` | Element Plus | 文件上传 |
| `@wangeditor/editor` | wangEditor | 富文本编辑器 |
| `md-editor-v3` | md-editor-v3 | Markdown 编辑器 |
| `monaco-editor` | Monaco Editor | 代码编辑器 |
| `echarts` / `echarts-gl` | ECharts 6 | 图表与 3D 可视化 |
| `vform3-builds` | VForm3 | 在线表单构建器 |
| `vue-plugin-hiprint` / `print-js` | hiprint | 打印与报表 |
| `@vue-office/pdf` / `excel` / `docx` | vue-office | Office 文件预览 |
| `logicflow` | LogicFlow | 流程图编辑 |
| `relation-graph` | relation-graph | 关系图可视化 |
| `json-editor-vue` | json-editor-vue | JSON 编辑器 |
| `vue-grid-layout` | vue-grid-layout | 网格拖拽布局 |
| `vue-draggable-plus` | vue-draggable-plus | 拖拽排序 |
| `splitpanes` | splitpanes | 分割面板 |
| `cropperjs` | cropperjs | 图片裁剪 |
| `xlsx-js-style` | xlsx-js-style | Excel 处理 |
| `mqtt` | mqtt 5 | MQTT 物联网通讯 |
| `sm-crypto-v2` | sm-crypto-v2 | 国密 SM2/SM3/SM4 |

---

## 样式与主题

- **CSS 预处理器：** SASS
- **主题方案：** Element Plus 主题变量 + 自定义 CSS 变量
- **暗黑模式：** 支持亮色/暗色主题切换
- **布局模式：** 支持多种布局（经典、横向、分栏、混合）

```scss
// 自定义主题变量示例
:root {
    --el-color-primary: #409eff;
    --next-bg-main-color: #f0f2f5;
}
```

---

