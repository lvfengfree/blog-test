<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import pinyin from "pinyin";

interface Article {
  title: string;
  introduction: string;
  link: string;
  slug: string;
  word?: string;
  put_time?: string;
  content?: string; // 正文内容
  text_pinyin?: string;
}

const router = useRouter();

const articles = ref<Article[]>([]);
const selectedArticle = ref<Article | null>(null);
const showNewArticleForm = ref(false);
const loading = ref(false);
const errorMsg = ref("");

const newArticle = reactive({
  title: "",
  introduction: "",
  link: "",
  content: "", // 正文内容
  put_time: "",
  word: "",
  text_pinyin: "",
});

// 解析 link，获取 slug（链接的最后一段路径）
function extractSlug(link: string) {
  if (!link) return "";
  return link.trim().replace(/\/$/, "").split("/").pop() || "";
}

// 生成拼音字符串
function getPinyin(text: string): string {
  const py = pinyin(text, {
    style: pinyin.STYLE_NORMAL,
    heteronym: false,
  });
  return py.flat().join("-");
}

// 获取文章列表
async function fetchArticles() {
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await fetch("http://localhost:5000/api/getWordList", {
      method: "GET",
      credentials: "include",
    });
    if (!res.ok) throw new Error("请求失败");
    const data = await res.json();
    articles.value = data.map((item: any) => ({
      title: item.title,
      introduction: item.introduction,
      link: item.link,
      slug: extractSlug(item.link),
      word: item.word,
      put_time: item.put_time,
      content: item.word || "", // 这里确保 content 有数据
      text_pinyin: item.text_pinyin || "",
    }));
  } catch (e) {
    errorMsg.value = "获取文章列表失败：" + (e as Error).message;
  } finally {
    loading.value = false;
  }
}

// 选择文章编辑（深拷贝，防止响应式问题）
function selectArticle(article: Article) {
  selectedArticle.value = JSON.parse(JSON.stringify(article));
  showNewArticleForm.value = false;
  errorMsg.value = "";
}

// 显示新建文章表单
function openNewArticleForm() {
  showNewArticleForm.value = true;
  selectedArticle.value = null;
  newArticle.title = "";
  newArticle.introduction = "";
  newArticle.link = "";
  newArticle.content = "";
  newArticle.put_time = "";
  newArticle.word = "";
  newArticle.text_pinyin = "";
  errorMsg.value = "";
}

// 校验文章必填字段
function validateArticle(article: {
  title: string;
  introduction: string;
  link: string;
  content?: string;
}) {
  if (!article.title.trim()) {
    errorMsg.value = "标题不能为空";
    return false;
  }
  if (!article.introduction.trim()) {
    errorMsg.value = "简介不能为空";
    return false;
  }
  if (!article.link.trim()) {
    errorMsg.value = "链接名称不能为空";
    return false;
  }
  if (!article.content || !article.content.trim()) {
    errorMsg.value = "正文内容不能为空";
    return false;
  }
  errorMsg.value = "";
  return true;
}

// 判断标题是否存在
function isTitleExists(title: string): boolean {
  return articles.value.some(article => article.title === title);
}

// 判断链接是否存在
function isLinkExists(link: string): boolean {
  return articles.value.some(article => article.link === link);
}

// 保存新建文章
async function saveNewArticle() {
  if (!validateArticle(newArticle)) return;

  // 先检查标题和链接是否已存在
  if (isTitleExists(newArticle.title)) {
    errorMsg.value = "文章标题已存在，请更换";
    return;
  }
  if (isLinkExists(newArticle.link)) {
    errorMsg.value = "文章链接已存在，请更换";
    return;
  }

  loading.value = true;

  // 自动生成 text_pinyin
  newArticle.text_pinyin = getPinyin(newArticle.title);

  // 同步正文内容到 word 字段
  newArticle.word = newArticle.content;

  try {
    const res = await fetch("http://localhost:5000/api/article", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify(newArticle),
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.message || "保存失败");
    }
    await fetchArticles();
    showNewArticleForm.value = false;
  } catch (e) {
    errorMsg.value = "保存文章失败：" + (e as Error).message;
  } finally {
    loading.value = false;
  }
}

// 保存编辑文章
async function saveArticle() {
  if (!selectedArticle.value) return;
  if (!validateArticle(selectedArticle.value)) return;
  loading.value = true;

  // 自动生成 text_pinyin
  selectedArticle.value.text_pinyin = getPinyin(selectedArticle.value.title);

  // 同步正文内容到 word 字段
  selectedArticle.value.word = selectedArticle.value.content || "";

  try {
    const res = await fetch(
      `http://localhost:5000/api/article/${selectedArticle.value.slug}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(selectedArticle.value),
      }
    );
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.message || "更新失败");
    }
    await fetchArticles();
  } catch (e) {
    errorMsg.value = "更新文章失败：" + (e as Error).message;
  } finally {
    loading.value = false;
  }
}

// 删除文章
async function deleteArticle(title: string) {
  if (!confirm(`确定删除文章《${title}》吗？`)) return;
  loading.value = true;
  errorMsg.value = "";
  try {
    const res = await fetch(`http://localhost:5000/api/article/${encodeURIComponent(title)}`, {
      method: "DELETE",
      credentials: "include",
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.message || "删除失败");
    }
    // 删除后如果删除的是当前选中文章，清空编辑区
    if (selectedArticle.value && selectedArticle.value.title === title) {
      selectedArticle.value = null;
    }
    await fetchArticles();
  } catch (e) {
    errorMsg.value = "删除文章失败：" + (e as Error).message;
  } finally {
    loading.value = false;
  }
}

// 登出逻辑
function logout() {
  localStorage.removeItem("isLoggedIn");
  router.push("/login");
}

onMounted(() => {
  fetchArticles();
});
</script>

<template>
  <div class="dash-wrapper">
    <nav class="nav-bar">
      <button @click="router.push('/')">首页</button>
      <button @click="logout">登出</button>
    </nav>

    <div class="content">
      <aside class="sidebar">
        <button class="new-article-btn" @click="openNewArticleForm">新建文章</button>
        <div class="articles-list">
          <p v-if="loading">加载中...</p>
          <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
          <ul>
            <li
              v-for="article in articles"
              :key="article.slug"
                :class="{ active: selectedArticle && selectedArticle.slug === article.slug }"
              @click="selectArticle(article)"
              style="cursor: pointer;"
              >
                {{ article.title }}
            </li>
          </ul>
        </div>
      </aside>

      <main class="editor">
        <h2 v-if="showNewArticleForm">新建文章</h2>
        <h2 v-else-if="selectedArticle">编辑文章</h2>
        <h2 v-else>请选择文章或新建</h2>

        <div v-if="showNewArticleForm">
          <input
            v-model="newArticle.title"
            placeholder="标题"
            type="text"
          />
          <input
            v-model="newArticle.introduction"
            placeholder="简介"
            type="text"
          />
          <input
            v-model="newArticle.link"
            placeholder="文章链接名称（例如 exam）"
            type="text"
          />
          <textarea
            v-model="newArticle.content"
            placeholder="正文内容"
            rows="10"
          />
          <button @click="saveNewArticle" :disabled="loading">保存</button>
        </div>

        <div v-else-if="selectedArticle">
          <input
            v-model="selectedArticle.title"
            placeholder="标题"
            type="text"
          />
          <input
            v-model="selectedArticle.introduction"
            placeholder="简介"
            type="text"
          />
          <input
            v-model="selectedArticle.link"
            placeholder="文章链接名称（例如 exam）"
            type="text"
          />
          <textarea
            v-model="selectedArticle.content"
            placeholder="正文内容"
            rows="10"
          />
          <div style="margin-top: 10px;">
            <button @click="saveArticle" :disabled="loading">保存</button>
            <button @click="deleteArticle(selectedArticle.title)" :disabled="loading" style="margin-left: 10px; background-color: #e74c3c; color: white; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer;">
              删除
            </button>
          </div>
        </div>

        <p class="error" v-if="errorMsg">{{ errorMsg }}</p>
      </main>
    </div>
  </div>
</template>

<style scoped>
.dash-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.nav-bar {
  display: flex;
  justify-content: flex-end;
  background-color: #409eff;
  padding: 10px;
  gap: 10px;
}

.nav-bar button {
  background: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 280px;
  background: #f5f7fa;
  border-right: 1px solid #ddd;
  padding: 10px;
  display: flex;
  flex-direction: column;
}

.new-article-btn {
  margin-bottom: 10px;
  background-color: #409eff;
  color: white;
  border: none;
  padding: 10px;
  font-weight: 700;
  border-radius: 6px;
  cursor: pointer;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 8px rgb(64 158 255 / 0.3);
}

.articles-list {
  overflow-y: auto;
  flex: 1;
  color: black;
}

.articles-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
  color: black;
}

.articles-list li {
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 12px;
  margin-bottom: 6px;
  backdrop-filter: blur(6px);
  background: rgba(255 255 255 / 0.6);
  transition: background-color 0.3s ease;
  user-select: none;
}

.articles-list li:hover,
.articles-list li.active {
  background-color: rgba(64, 158, 255, 0.6);
  color: white;
}

.editor {
  flex: 1;
  padding: 20px;
  background: #fff;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.editor input,
.editor textarea {
  width: 100%;
  padding: 8px 12px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  resize: vertical;
}

.editor button {
  width: 120px;
  align-self: flex-start;
  background-color: #409eff;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.editor button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.error {
  color: #e74c3c;
  font-weight: 600;
}
</style>
