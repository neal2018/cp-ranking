<template>
  <nav text-xl mt-6 inline-flex gap-2>
    <button icon-btn absolute top-10 right-10 @click="toggleDark()">
      <div dark:i-carbon-moon i-carbon-sun />
    </button>
  </nav>
</template>
