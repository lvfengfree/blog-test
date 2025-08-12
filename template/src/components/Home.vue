<template>
  <div id="box">
    <!-- 进入动画遮罩 -->
    <div v-if="showOverlay" class="fade-overlay"></div>
    <!-- 时间问候弹窗 -->
    <transition name="slide-down-fade">
      <div v-if="showGreeting" class="greeting-popup">
        {{ greetingText }}
      </div>
    </transition>

    <header class="navbar">
      <nav class="nav-left">
        <ul>
          <li class="active"><a href="https://lvfengfree.top">主页</a></li>
          <li class="active"><a href="https://openlist.lvfengfree.top">云盘</a></li>
          <li class="active"><a href="https://nezha.lvfengfree.top">服务器监控</a></li>
        </ul>
      </nav>
      <div class="nav-right">
        <button @click="onPublishClick">发布文章</button>
      </div>
    </header>

    <section class="hero-section">
      <div class="hero-overlay">
        <h1 class="typing-text">
          {{ displayText }}<span class="cursor">|</span>
        </h1>
        <p :class="{ 'fade-in': subtitleVisible }">
          自由的权力归众生<br />
          <span class="author">——Optimus Prime</span>
        </p>
        <div class="scroll-arrow" @click="scrollToArticles">
          <img src="../assets/arrow.png" alt="向下箭头" />
        </div>
      </div>
    </section>

    <section class="posts-title-section">
  <h2>✨ 发布的文章</h2>
</section>

<main class="main-content">

  <!-- 中间文章列表 -->
  <div id="articles" class="articles-grid">
    <article class="article-card" v-for="(post, index) in posts" :key="index">
      <div class="article-image">
        <img
          src="https://images.unsplash.com/photo-1503264116251-35a269479413?auto=format&fit=crop&w=1350&q=80"
          alt="文章图片"
        />
      </div>
      <div class="article-info">
        <h3>{{ post.title }}</h3>
        <p>{{ post.introduction }}</p>
        <router-link :to="`/article/${post.slug}`">阅读全文</router-link>
      </div>
    </article>
  </div>

  <!-- 右侧性能监控和天气 -->
</main>
     <footer class="footer-info">
      <div class="footer-container">
        <p>© 2025 旅风free博客 | <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">暂无备案</a>Powered by 旅风free</p>
        <p></p>
        <p>技术栈：Flask Vue3.js mysql</p>
      </div>
    </footer>
    <button
      v-show="showBackToTop"
      class="back-to-top"
      @click="scrollToTop"
      title="回到顶部"
      aria-label="回到顶部"
    >
      ↑
    </button>
  </div>
</template>

<script setup lang="ts" name="Home">
import { ref, onMounted, onUnmounted } from "vue";

interface WordItem {
  title: string;
  introduction: string;
  link: string;
}

const posts = ref<WordItem[]>([]);

const displayText = ref("");
const fullText = "欢迎来到旅风free的博客";
const subtitleVisible = ref(false);
const showOverlay = ref(true);

const showBackToTop = ref(false);
// 弹窗相关
const showGreeting = ref(false)
const greetingText = ref("")

function getGreetingByHour(hour: number): string {
  if (hour >= 5 && hour < 9)
    return "早上好，祝你今天有个美好的开始！";
  else if (hour >= 9 && hour < 12)
    return "上午好，工作顺利，别忘了喝杯水哦！";
  else if (hour >= 12 && hour < 14)
    return "中午好，记得好好休息，享用午餐！";
  else if (hour >= 14 && hour < 18)
    return "下午好，保持状态，努力到傍晚！";
  else if (hour >= 18 && hour < 22)
    return "晚上好，放松一下，给自己充充电吧！";
  else
    return "凌晨好，夜深了，注意休息，晚安！";
}
import { useRouter } from 'vue-router';

const router = useRouter();

function onPublishClick() {
  const loggedIn = localStorage.getItem('isLoggedIn') === 'true';
  if (loggedIn) {
    router.push('/dash');
  } else {
    router.push('/login');
  }
}
async function fetchPosts() {
  try {
    const res = await fetch("http://localhost:5000/api/getWordList", {
      method: "GET",
    });
    if (!res.ok) throw new Error("请求失败");
    const data = await res.json();
    posts.value = data.map((item: any) => {
      const slug = item.link.trim().replace(/\/$/, "").split("/").pop();
      return {
        title: item.title,
        introduction: item.introduction,
        link: item.link,
        slug: slug,
      };
    });
  } catch (error) {
    console.error("获取数据失败:", error);
  }
}

function scrollToArticles() {
  const el = document.getElementById("articles");
  if (el) {
    el.scrollIntoView({ behavior: "smooth" });
  }
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function typeEffect() {
  let i = 0;
  const timer = setInterval(() => {
    if (i < fullText.length) {
      displayText.value += fullText[i];
      i++;
    } else {
      clearInterval(timer);
      setTimeout(() => {
        subtitleVisible.value = true;
      }, 300);
    }
  }, 150);
}

function onScroll() {
  showBackToTop.value = window.scrollY > 300; // 滚动超过300px显示按钮
}

onMounted(() => {
  fetchPosts();
  typeEffect();
  greetingText.value = getGreetingByHour(new Date().getHours())
  showGreeting.value = true
setTimeout(() => {
  showGreeting.value = false
}, 3000)
  setTimeout(() => {
    showOverlay.value = false;
  }, 1500);

  window.addEventListener("scroll", onScroll);
});

onUnmounted(() => {
  window.removeEventListener("scroll", onScroll);
});
</script>

<style src="../assets/home.css">

</style>
<style>
@font-face {
  font-family: 'HarmonyOS_Regular';
  src: url('../assets/HarmonyOS_Regular.f.woff2') format('woff2');
  font-weight: normal;
  font-style: normal;
}
</style>
