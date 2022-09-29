import submissions from '~/data/submissions.json'
import handles from '~/data/handles.json'

export const getPointFromRating = (rating: number, platform: string) => {
  if (platform === 'codeforces') {
    if (rating < 1000)
      return 0
    if (rating < 1500)
      return 1
    if (rating < 2000)
      return 2
    if (rating < 2500)
      return 3
    if (rating < 3000)
      return 4
    return 5
  }
  if (platform === 'atcoder') {
    if (rating < 800)
      return 0
    if (rating < 1200)
      return 1
    if (rating < 1600)
      return 2
    if (rating < 2000)
      return 3
    if (rating < 2400)
      return 4
    return 5
  }
  if (platform === 'icpc') {
    if (rating === 1)
      return 1
    return 0.8
  }
  return 0
}

const getPlatformPoints = (handle: string, platform: string) => {
  return submissions.reduce((acc, submission) => {
    if (submission.handle.toLowerCase() === handle.toLowerCase()
    && submission.platform === platform)
      return acc + getPointFromRating(submission.rating, platform)
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
  const atcoderPoints = handle?.atcoder_handles.reduce((acc, handle) => {
    return acc + getPlatformPoints(handle, 'atcoder')
  }, 0) ?? 0
  const icpcPoints = handle?.codeforces_handles.reduce((acc, handle) => {
    return acc + getPlatformPoints(handle, 'icpc')
  }, 0) ?? 0
  return {
    codeforces: codeforcesPoints,
    codeforcesUnknown: codeforcesUnknownCount,
    atcoder: atcoderPoints,
    icpc: icpcPoints,
    total: codeforcesPoints + atcoderPoints + icpcPoints,
  }
}

export const getTableData = () => {
  const tableData = handles.map((handle) => {
    // TODO: improve time complexity
    const { codeforces, codeforcesUnknown, atcoder, icpc, total } = getPoints(handle.username)
    return {
      rank: 0,
      username: handle.username,
      codeforces,
      codeforcesUnknown,
      atcoder,
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
