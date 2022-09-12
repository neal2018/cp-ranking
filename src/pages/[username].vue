<script setup lang="ts">
import handles from '~/data/handles.json'
import submissions from '~/data/submissions.json'
import { getPointFromRating, getTableData } from '~/composables/utils'

const props = defineProps<{ username: string }>()
const router = useRouter()

// get the user submission history from submission.json
const handle = handles.find(handle => handle.username === props.username)!
const userCFSubmissions = submissions.filter(submission =>
  (submission.platform === 'codeforces' && handle.codeforces_handles.includes(submission.handle)))

const userATsubmissions = submissions.filter(submission =>
  (submission.platform === 'atcoder' && handle.atcoder_handles.includes(submission.handle)))

const userPoints = getTableData().find(user => user.username === props.username)!

const tableTitles = ['Platform', 'Handle', 'Contest ID', 'Problem ID', 'Rating', 'Solved Time', 'Points']

const formatTime = (s: number) => {
  return new Date(s * 1e3).toLocaleString('en-US', {
    timeZone: 'America/New_York',
    hour12: false,
  }).replace(', ', ' ').slice(0, -3)
}
</script>

<template>
  <div>
    <p text-4xl p-10>
      CP Ranking: {{ props.username }}
    </p>
    <div>
      <p text-3xl>
        Rank: {{ userPoints.rank }}; Total: {{ userPoints.total }} Points
      </p>
    </div>
    <div>
      <p text-2xl p-t-10>
        Codeforces: {{ userPoints.codeforces }} Points
      </p>
      <table border-1 m-auto m-y-5>
        <tr border-1>
          <th v-for="val in tableTitles" :key="val" border-1>
            {{ val }}
          </th>
        </tr>
        <tr v-for="(userData, index) in userCFSubmissions" :key="index" border-1>
          <td v-for="(val, key) in userData" :key="key" border-1>
            <span v-if="key === 'time'">
              {{ formatTime(val as number) }}
            </span>
            <span v-else-if="key === 'rating'">
              {{ val === -1 ? 'UNKNOWN' : val }}
            </span>
            <span v-else>
              {{ val }}
            </span>
          </td>
          <td border-1>
            {{ getPointFromRating(userData.rating, userData.platform) }}
          </td>
        </tr>
      </table>
    </div>

    <div>
      <p text-2xl p-t-10>
        AtCoder: {{ userPoints.atcoder }} Points
      </p>
      <table border-1 m-auto m-y-5>
        <tr border-1>
          <th v-for="val in tableTitles" :key="val" border-1>
            {{ val }}
          </th>
        </tr>
        <tr v-for="(userData, index) in userATsubmissions" :key="index" border-1>
          <td v-for="(val, key) in userData" :key="key" border-1>
            <span v-if="key === 'time'">
              {{ formatTime(val as number) }}
            </span>
            <span v-else>
              {{ val }}
            </span>
          </td>
          <td border-1>
            {{ getPointFromRating(userData.rating, userData.platform) }}
          </td>
        </tr>
      </table>
    </div>

    <div>
      <button
        class="btn m-3 text-sm mt-8"
        @click="router.back()"
      >
        Back
      </button>
    </div>
  </div>
</template>
