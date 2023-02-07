import submissions from '~/data/submissions.json'
import handles from '~/data/handles.json'

export const getPointFromProblemId = (problem_id: string, platform: string) => {
  if (platform === 'codeforces') {
    var letter = problem_id[0]
    if (letter === 'A')
      return 0.25
    if (letter === 'B')
      return 0.5
    if (letter === 'C')
      return 1
    if (letter === 'D')
      return 1.5
    if (letter === 'E')
      return 2
    if (letter === 'F')
      return 4
    if (letter === 'G')
      return 6
    return 8
  }
  if (platform === 'icpc') {
    return 1
  }
  return 0
}

export const getDivisionMultiplier = (division: int, platform: string) => {
  if (platform === 'codeforces') {
    if (division === 1)
      return 4
    if (division === 2)
      return 1
    if (division === 3)
      return 0.25
    if (division === 4)
      return 0.125
    return 1
  }
  return 1
}

export const getPartMultiplier = (problem_id: string, platform: string) => {
  if (platform === 'codeforces')
    return (problem_id.length > 1 ? 0.5 : 1)
  return 1
}

export const getUpsolveMultiplierFromTimestamp = (submission_time: number, contest_end_time: number) => {
  return submission_time < contest_end_time ? 1 : (submission_time <= contest_end_time + 604800 ? 0.5 : 0)
}

const getPlatformPoints = (handle: string, platform: string) => {
  return submissions.reduce((acc, submission) => {
    if (submission.handle.toLowerCase() === handle.toLowerCase()
      && submission.platform === platform)
      return acc + getUpsolveMultiplierFromTimestamp(submission.submission_time, submission.contest_end_time) * getDivisionMultiplier(submission.division, platform) * getPartMultiplier(submission.problem_id, platform) * getPointFromProblemId(submission.problem_id, platform)
    return acc
  }, 0)
}

const getPlatformUnknownCount = (handle: string, platform: string) => {
  return submissions.reduce((acc, submission) => {
    if (submission.handle.toLowerCase() === handle.toLowerCase()
      && submission.platform === platform)
      return acc + (submission.rating === -1 ? 1 : 0)
    return acc
  }, 0)
}

export const getPoints = (username: string) => {
  const handle = handles.find(handle => handle.username === username)
  const codeforcesPoints = handle?.codeforces_handles.reduce((acc, handle) => {
    return acc + getPlatformPoints(handle, 'codeforces')
  }, 0) ?? 0
  const codeforcesUnknownCount = handle?.codeforces_handles.reduce((acc, handle) => {
    return acc + getPlatformUnknownCount(handle, 'codeforces')
  }, 0) ?? 0
  const icpcPoints = handle?.codeforces_handles.reduce((acc, handle) => {
    return acc + getPlatformPoints(handle, 'icpc')
  }, 0) ?? 0
  return {
    codeforces: codeforcesPoints,
    codeforcesUnknown: codeforcesUnknownCount,
    icpc: icpcPoints,
    total: codeforcesPoints + icpcPoints,
  }
}

export const getTableData = () => {
  const tableData = handles.map((handle) => {
    // TODO: improve time complexity
    const { codeforces, codeforcesUnknown, icpc, total } = getPoints(handle.username)
    return {
      rank: 0,
      username: handle.username,
      codeforces,
      codeforcesUnknown,
      icpc,
      total,
    }
  })

  tableData.sort((a, b) => b.total - a.total)

  // add rank to tableData, same total should has the same rank
  let rank = 1
  let lastTotal = tableData[0].total
  tableData.forEach((item, index) => {
    if (item.total < lastTotal) {
      rank = index + 1
      lastTotal = item.total
    }
    item.rank = rank
  })

  return tableData
}
