<script setup lang="ts">
import handles from '~/data/handles.json'
import { getPoints } from '~/composables/utils'

const tableTitles = ['Rank', 'User', 'CodeForces', 'AtCoder', 'Total']

const tableData = handles.map((handle, index) => {
  // TODO: improve time complexity
  const { codeforces, atcoder, total } = getPoints(handle.username)
  return {
    rank: 0,
    username: handle.username,
    codeforces,
    atcoder,
    total,
  }
})

tableData.sort((a, b) => b.total - a.total)

// add rank to tableData, same total should has the same rank
;(() => {
  let rank = 1
  let lastTotal = tableData[0].total
  tableData.forEach((item, index) => {
    if (item.total < lastTotal) {
      rank = index + 1
      lastTotal = item.total
    }
    item.rank = rank
  })
})()
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
        <tr v-for="(userData, index) in tableData" :key="index" border-1>
          <td v-for="(val, key) in userData" :key="key" border-1>
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
