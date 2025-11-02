import { createRouter, createWebHistory } from 'vue-router'
import ArticleList from '../views/ArticleList.vue'
import ArticleDetail from '../views/ArticleDetail.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/articles'
    },
    {
      path: '/articles',
      name: 'ArticleList',
      component: ArticleList
    },
    {
      path: '/articles/:id',
      name: 'ArticleDetail',
      component: ArticleDetail
    },

  ],
})

export default router
