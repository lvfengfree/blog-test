<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const username = ref("");
const password = ref("");
const errorMsg = ref("");

async function onLogin() {
  errorMsg.value = "";
  if (!username.value.trim()) {
    errorMsg.value = "用户名不能为空";
    return;
  }
  if (!password.value.trim()) {
    errorMsg.value = "密码不能为空";
    return;
  }

  try {
    const res = await fetch("http://localhost:5000/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",  // 允许携带 cookie
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    });

    const data = await res.json();

    if (res.ok) {
      // 登录成功，跳转到 /dash 页面
      router.push("/dash");
    } else {
      errorMsg.value = data.message || "登录失败";
    }
  } catch (error) {
    errorMsg.value = "网络异常，请稍后重试";
    console.error("请求异常:", error);
  }
}
</script>

<template>
  <div class="login-wrapper">
    <div class="login-box">
      <h2>用户登录</h2>
      <input
        v-model="username"
        type="text"
        placeholder="请输入用户名"
        autocomplete="username"
      />
      <input
        v-model="password"
        type="password"
        placeholder="请输入密码"
        autocomplete="current-password"
      />
      <button @click="onLogin">登录</button>
      <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<style scoped>
.login-wrapper {
  height: 100vh;
  background: linear-gradient(135deg, #1e1e2f, #27293d);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.login-box {
  width: 320px;
  background: rgba(255 255 255 / 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 40px 30px;
  box-shadow: 0 8px 32px rgba(64, 158, 255, 0.2);
  color: #eee;
  display: flex;
  flex-direction: column;
  gap: 20px;
  text-align: center;
}

.login-box h2 {
  margin-bottom: 10px;
  font-weight: 700;
  font-size: 1.8rem;
}

.login-box input {
  padding: 12px 15px;
  border: none;
  border-radius: 12px;
  background: rgba(255 255 255 / 0.15);
  color: #ddd;
  font-size: 1rem;
  outline: none;
  transition: background-color 0.3s ease;
}

.login-box input::placeholder {
  color: #bbb;
}

.login-box input:focus {
  background: rgba(64, 158, 255, 0.3);
  color: white;
}

.login-box button {
  padding: 12px;
  border-radius: 20px;
  border: none;
  background: linear-gradient(90deg, #409eff, #66b1ff);
  color: white;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.2s ease;
}

.login-box button:hover {
  background: linear-gradient(90deg, #66b1ff, #409eff);
  transform: translateY(-2px);
}

.error-msg {
  color: #ff6b6b;
  font-weight: 600;
  margin-top: -10px;
  font-size: 0.9rem;
  min-height: 24px;
}
</style>
