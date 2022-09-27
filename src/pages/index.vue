<script setup lang="ts">
import { getTableData } from '~/composables/utils'

const tableTitles = ['Rank', 'User', 'Codeforces', 'AtCoder', 'ICPC', 'Total']
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
          <td v-for="(val, key) in userData" :key="key" border-1>
            <span v-if="key === 'username'" cursor-pointer @click="go(val as string)">
              {{ val }}
            </span>
            <span v-else-if="key === 'total' || key === 'icpc'">
              {{ (val as number).toFixed(1) }}
            </span>
            <span v-else>
              {{ val }}
            </span>
          </td>
        </tr>
      </table>
    </div>
    <div right border-1 max-w-sm p-2 self-end>
      <p text-sm text-left>
        * Note: Currently only record points gained during live contests in Codeforces and AtCoder
      </p>
    </div>
  </div>
</template>
