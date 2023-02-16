<script setup lang="ts">
import { getTableData } from '~/composables/utils'

const tableTitles = ['Rank', 'User', 'Codeforces', 'ICPC', 'Total']
const tableData = getTableData()
const router = useRouter()

const go = (username: string) => {
  if (username)
    router.push(`/${encodeURIComponent(username)}`)
}
</script>

<template>
  <div relative flex flex-col>
    <p text-4xl p-10>
      CP Ranking
    </p>
    <div text-4>
      <table border-1 m-auto m-y-5>
        <tr border-1>
          <th v-for="val in tableTitles" :key="val" border-1>
            {{ val }}
          </th>
        </tr>
        <tr v-for="(userData, index) in tableData" :key="index" border-1>
          <td border-1>
            {{ userData.rank }}
          </td>
          <td border-1>
            <span cursor-pointer @click="go(userData.username)">
              {{ userData.username }}
            </span>
          </td>
          <td border-1>
            <p relative>
              {{ userData.codeforces }}
            </p>
          </td>
          <td border-1 px-6>
            {{ userData.icpc.toFixed(1) }}
          </td>
          <td border-1>
            <p relative px-6>
              {{ userData.total.toFixed(1) }}
            </p>
          </td>
        </tr>
      </table>
    </div>
    <div right border-1 max-w-sm p-2 self-end>
      <p text-sm text-left>
        * Note: Currently only record points gained during live contests in Codeforces and during ICPC practice contests. Feel free to send pull requests to improve this page.
      </p>
    </div>
  </div>
</template>
