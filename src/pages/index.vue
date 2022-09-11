<script setup lang="ts">
import handles from '~/data/handles.json'
import { getPoints } from '~/composables/utils'

const tableTitles = ['Rank', 'User', 'CodeForces', 'AtCoder', 'Total']
</script>

<template>
  <div relative>
    <p text-4xl>
      CP Ranking
    </p>
    <div text-4>
      <table border-1 m-auto p-10 m-y-10 v>
        <tr border-1>
          <th v-for="val in tableTitles" :key="val" border-1>
            {{ val }}
          </th>
        </tr>
        <tr v-for="(item, i) in handles" :key="item.username" border-1>
          <td border-1>
            {{ i + 1 }}
          </td>
          <td border-1>
            {{ item.username }}
          </td>
          <td v-for="(val, key) in getPoints(item.username)" :key="key" border-1>
            {{ val }}
          </td>
        </tr>
      </table>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300&display=swap');
*{
  font-family: 'Fira Code', monospace;
}
table,
th,
td {
  padding: 0.5rem;
}
</style>
