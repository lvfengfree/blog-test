<template>
  <div>
    <!-- 顶部导航栏 -->
    <header class="navbar" v-show="showPage" v-bind:class="{fadeIn: showPage}">
      <nav class="nav-left">
        <ul>
          <li class="active"><a href="https://lvfengfree.top">主页</a></li>
          <li><a href="https://openlist.lvfengfree.top">云盘</a></li>
          <li><a href="https://nezha.lvfengfree.top">服务器监控</a></li>
        </ul>
      </nav>
      <div class="nav-right">
        <button>发布文章</button>
      </div>
    </header>

    <!-- 顶部背景带标题 -->
    <section class="header-banner" v-show="showPage" v-bind:class="{fadeIn: showPage}">
      <h1 class="banner-title" :class="{ titleAppear: showPage }">
        {{ article?.title || '加载中...' }}
      </h1>
    </section>

    <main>
      <div v-if="article" class="article-container">
        <!-- 渲染Markdown转换的HTML -->
        <div
          v-html="renderedMarkdown"
          class="article-content"
          ref="articleContent"
        ></div>
      </div>
      <div v-else class="loading-text">加载中...</div>
    </main>

    <!-- 固定底部信息栏 -->
    <footer class="footer-info" v-show="showPage" v-bind:class="{fadeIn: showPage}">
      <div class="footer-content">
        <span>备案号：粤ICP备12345678号</span>
        <span>Powered by 旅风free</span>
        <span>© 2025</span>
      </div>
    </footer>

    <!-- 返回上一页按钮 -->
    <button
      class="back-btn"
      v-show="showBackButton"
      @click="goBack"
      title="返回上一页"
    >
      ← 返回
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import MarkdownIt from "markdown-it";
import Prism from "prismjs";

// 导入需要的语言支持，比如JavaScript、TypeScript、CSS等
import "prismjs/components/prism-javascript";
import "prismjs/components/prism-typescript";
import "prismjs/components/prism-css";
// 导入Prism主题样式
import "prismjs/themes/prism-tomorrow.css";

interface ArticleType {
  title: string;
  introduction: string;
  link: string;
  put_time: string;
  text_pinyin: string;
  word: string;
}

const route = useRoute();
const router = useRouter();
const article = ref<ArticleType | null>(null);
const renderedMarkdown = ref("");
const showPage = ref(false);
const showBackButton = ref(false);
const articleContent = ref<HTMLElement | null>(null);

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: (code, lang) => {
    if (lang && Prism.languages[lang]) {
      try {
        return `<pre class="language-${lang}"><code>${Prism.highlight(code, Prism.languages[lang], lang)}</code></pre>`;
      } catch {
        // 高亮失败，返回转义后的代码
        return `<pre class="language-"><code>${md.utils.escapeHtml(code)}</code></pre>`;
      }
    }
    return `<pre class="language-"><code>${md.utils.escapeHtml(code)}</code></pre>`;
  }
});

async function fetchArticle(slug: string) {
  try {
    showPage.value = false; // 关闭显示，准备加载动画
    const res = await fetch(`http://localhost:5000/api/article/${slug}`);
    if (!res.ok) throw new Error("加载失败");
    const data = await res.json();
    article.value = data;
    renderedMarkdown.value = md.render(data.word || "");
    await nextTick(); // 等DOM更新后启动滚动动画观察器
    initScrollAnimations();
    showPage.value = true; // 显示页面
  } catch (e) {
    console.error(e);
  }
}

function initScrollAnimations() {
  if (!articleContent.value) return;

  const elements = articleContent.value.querySelectorAll(
    "p, h1, h2, h3, h4, h5, h6, pre, blockquote, ul, ol"
  );
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("fadeInUp");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );

  elements.forEach((el) => {
    el.classList.add("beforeFade"); // 初始隐藏样式
    observer.observe(el);
  });
}

function goBack() {
  if (window.history.length > 1) {
    window.history.back();
  } else {
    router.push("/"); // 没历史就回首页
  }
}

onMounted(() => {
  const slug = route.params.slug as string;
  if (slug) fetchArticle(slug);

  // 判断是否显示返回按钮（有历史或路由深度大）
  showBackButton.value =
    window.history.length > 1 || router.currentRoute.value.path !== "/";
});

watch(
  () => route.params.slug,
  (newSlug) => {
    if (typeof newSlug === "string") fetchArticle(newSlug);
  }
);
</script>

<style scoped>
/* 顶部导航栏 */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  color: white;
  padding: 0 20px;
  height: 50px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  position: sticky;
  top: 0;
  z-index: 1000;
  opacity: 0;
  transition: opacity 0.6s ease;
}

.navbar.fadeIn {
  opacity: 1;
}

.nav-left ul {
  display: flex;
  list-style: none;
  gap: 20px;
  margin: 0;
  padding: 0;
}

.nav-left li {
  line-height: 50px;
  cursor: pointer;
  padding: 0 10px;
  border-radius: 6px;
  transition: background-color 0.3s, transform 0.2s;
}

.nav-left li:hover {
  background-color: rgba(64, 158, 255, 0.8);
  transform: scale(1.05);
}

.nav-right button {
  background: linear-gradient(90deg, #409eff, #66b1ff);
  border: none;
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.3s, transform 0.2s;
}

.nav-right button:hover {
  background: linear-gradient(90deg, #66b1ff, #409eff);
  transform: translateY(-2px);
}

/* 顶部背景带标题 */
.header-banner {
  position: relative;
  height: 200px;
  padding-top: 50px;
  background-image: url('../assets/info.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.6s ease 0.3s;
}
.header-banner::before {
  content: "";
  position: absolute;
  inset: 0; /* top:0; right:0; bottom:0; left:0; */
  background: rgba(0, 0, 0, 0.5); /* 半透明黑色遮罩，可以调节透明度 */
  z-index: 1;
  pointer-events: none; /* 不阻止鼠标事件 */
}
.header-banner.fadeIn {
  opacity: 1;
}

@keyframes fadeInUpTitle {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.banner-title {
  position: relative;
  z-index: 2;
  font-size: 2.4rem;
  font-weight: 700;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.7);
  text-align: center;
  padding: 0 20px;
  opacity: 0; /* 初始透明 */
  transform: translateY(20px); /* 初始向下偏移 */
  transition: opacity 0.6s ease, transform 0.6s ease;
}

/* showPage为true时触发动画 */
.titleAppear {
  animation: fadeInUpTitle 0.6s forwards;
}

/* 文章容器 */
.article-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  color: #eee;
  padding-bottom: 70px;
}

/* Markdown内容样式 */
.article-content {
  line-height: 1.8;
  font-size: 1.1rem;
  color: #ddd;
}

/* 加载提示 */
.loading-text {
  text-align: center;
  color: #aaa;
  font-size: 1.2rem;
  margin: 50px 0;
}

/* 代码块样式 */
.article-content pre {
  background: #1e1e1e;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
}

/* 代码文字颜色 */
.article-content code {
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 0.95rem;
  color: #ddd;
}

/* 底部固定栏 */
.footer-info {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  color: #ccc;
  padding: 15px 20px;
  text-align: center;
  font-size: 0.9rem;
  display: flex;
  justify-content: center;
  gap: 20px;
  opacity: 0;
  transition: opacity 0.6s ease 0.5s;
}

.footer-info.fadeIn {
  opacity: 1;
}

/* 返回上一页按钮 */
.back-btn {
  position: fixed;
  bottom: 80px;
  right: 20px;
  background: #409eff;
  border: none;
  color: white;
  padding: 10px 15px;
  border-radius: 24px;
  cursor: pointer;
  font-weight: 700;
  font-size: 1rem;
  box-shadow: 0 4px 8px rgb(64 158 255 / 0.5);
  transition: background-color 0.3s ease, transform 0.2s ease;
  z-index: 2000;
}

.back-btn:hover {
  background: #66b1ff;
  transform: scale(1.05);
}

/* 滚动进入视口动画初始状态 */
.beforeFade {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

/* 滚动进入视口动画激活状态 */
.fadeInUp {
  opacity: 1 !important;
  transform: translateY(0) !important;
}
</style>
