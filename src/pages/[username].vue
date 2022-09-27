<script setup lang="ts">
import handles from '~/data/handles.json'
import submissions from '~/data/submissions.json'
import { getPointFromRating, getTableData } from '~/composables/utils'

const props = defineProps<{ username: string }>()
const router = useRouter()

const userPoints = getTableData().find(user => user.username === props.username)!

const tableTitles = ['Platform', 'Handle', 'Contest ID', 'Problem ID', 'Rating', 'Solved Time', 'Points']

const formatTime = (s: number) => {
  return new Date(s * 1e3).toLocaleString('en-US', {
    timeZone: 'America/New_York',
    hour12: false,
  }).replace(', ', ' ').slice(0, -3)
}

// get the user submission history from submission.json
const handle = handles.find(handle => handle.username === props.username)!
const userCFSubmissions = submissions.filter(submission =>
  (submission.platform === 'codeforces' && handle.codeforces_handles.includes(submission.handle)))

const userATsubmissions = submissions.filter(submission =>
  (submission.platform === 'atcoder' && handle.atcoder_handles.includes(submission.handle)))

const userICPCsubmissions = submissions.filter(submission =>
  (submission.platform === 'icpc' && handle.codeforces_handles.includes(submission.handle))).reverse()
</script>

<template>
  <div>
    <p text-4xl p-10>
      CP Ranking: {{ props.username }}
    </p>
    <div>
      <p text-3xl>
        Rank: {{ userPoints.rank }}; Total: {{ userPoints.total.toFixed(1) }} Points
      </p>
    </div>
    <div>
      <p text-2xl p-t-10>
        Codeforces: {{ handle.codeforces_handles }}; {{ userPoints.codeforces }} Points
      </p>
      <table border-1 m-auto m-y-5>
        <tr border-1>
          <th v-for="val in tableTitles" :key="val" border-1>
            {{ val }}
          </th>
        </tr>
        <tr v-for="(userData, index) in userCFSubmissions" :key="index" border-1>
          <td border-1>
            {{ userData.platform }}
          </td>
          <td border-1>
            <a :href="`https://codeforces.com/profile/${userData.handle}`" target="_blank">
              {{ userData.handle }}
            </a>
          </td>
          <td border-1>
            <a :href="`https://codeforces.com/contest/${userData.contest_id}`" target="_blank">
              {{ userData.contest_id }}
            </a>
          </td>
          <td border-1>
            <a :href="`https://codeforces.com/contest/${userData.contest_id}/problem/${userData.problem_id}`" target="_blank">
              {{ userData.problem_id }}
            </a>
          </td>
          <td border-1>
            {{ userData.rating === -1 ? 'UNKNOWN' : userData.rating }}
          </td>
          <td border-1>
            <a :href="`https://codeforces.com/contest/${userData.contest_id}/submission/${userData.submission_id}`" target="_blank">
              {{ formatTime(userData.time) }}
            </a>
          </td><td border-1>
            {{ userData.rating === -1 ? '?' : getPointFromRating(userData.rating, userData.platform) }}
          </td>
        </tr>
      </table>
    </div>

    <div>
      <p text-2xl p-t-10>
        AtCoder: {{ handle.atcoder_handles }}; {{ userPoints.atcoder }} Points
      </p>
      <table border-1 m-auto m-y-5>
        <tr border-1>
          <th v-for="val in tableTitles" :key="val" border-1>
            {{ val }}
          </th>
        </tr>
        <tr v-for="(userData, index) in userATsubmissions" :key="index" border-1>
          <td border-1>
            {{ userData.platform }}
          </td>
          <td border-1>
            <a :href="`https://atcoder.jp/users/${userData.handle}`" target="_blank">
              {{ userData.handle }}
            </a>
          </td>
          <td border-1>
            <a :href="`https://atcoder.jp/contests/${userData.contest_id}`" target="_blank">
              {{ userData.contest_id }}
            </a>
          </td>
          <td border-1>
            <a :href="`https://atcoder.jp/contests/${userData.contest_id}/tasks/${userData.problem_id}`" target="_blank">
              {{ userData.problem_id }}
            </a>
          </td>
          <td border-1>
            {{ userData.rating }}
          </td>
          <td border-1>
            <a :href="`https://atcoder.jp/contests/${userData.contest_id}/submissions/${userData.submission_id}`" target="_blank">
              {{ formatTime(userData.time) }}
            </a>
          </td>
          <td border-1>
            {{ getPointFromRating(userData.rating, userData.platform) }}
          </td>
        </tr>
      </table>
    </div>

    <div>
      <p text-2xl p-t-10>
        ICPC: {{ handle.codeforces_handles }}; {{ userPoints.icpc.toFixed(1) }} Points
      </p>
      <table border-1 m-auto m-y-5>
        <tr border-1>
          <th v-for="val in tableTitles" :key="val" border-1>
            {{ val }}
          </th>
        </tr>
        <tr v-for="(userData, index) in userICPCsubmissions" :key="index" border-1>
          <td border-1>
            {{ userData.platform }}
          </td>
          <td border-1>
            <a :href="`https://codeforces.com/profile/${userData.handle}`" target="_blank">
              {{ userData.handle }}
            </a>
          </td>
          <td border-1>
            <a :href="`https://codeforces.com/gym/${userData.contest_id}`" target="_blank">
              {{ userData.contest_id }}
            </a>
          </td>
          <td border-1>
            <a :href="`https://codeforces.com${userData.problem_id}`" target="_blank">
              {{ userData.problem_id }}
            </a>
          </td>
          <td border-1>
            {{ userData.rating }}
          </td>
          <td border-1>
            {{ formatTime(userData.time) }}
          </td><td border-1>
            {{ userData.rating === -1 ? '?' : getPointFromRating(userData.rating, userData.platform) }}
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
