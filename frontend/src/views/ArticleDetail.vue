<template>
    <div>
        <h1>Article Detail</h1>
        <p>Article ID: {{ route.params.id }}</p>
    </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>