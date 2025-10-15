<template>
    <div id="app">
      <ArticleList />
    </div>
</template>

<script setup>
import ArticleList from './ArticleList.vue';
import { onMounted } from 'vue';
import { signInAndGetJwt } from '../stackClient';

onMounted(async () => {
  const jwt = await signInAndGetJwt('cdmisbach@icloud.com', 'testingpassword123');
  console.log('JWT:', jwt);
});


</script>

<style scoped>
.about {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
</style>