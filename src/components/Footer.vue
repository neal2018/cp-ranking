<template>
  <nav text-xl inline-flex gap-2 absolute top-10 right-5>
    <button icon-btn @click="toggleDark()">
      <div dark:i-carbon-moon i-carbon-sun />
    </button>
    <a
      icon-btn i-carbon-logo-github
      rel="noreferrer"
      href="https://github.com/neal2018/cp-ranking"
      target="_blank"
      title="GitHub"
    />
  </nav>
</template>
