import submissions from '~/data/submissions.json'
import handles from '~/data/handles.json'

const getPointFromRating = (rating: number, platform: string) => {
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

export const getPoints = (username: string) => {
  const handle = handles.find(handle => handle.username === username)
  const codeforcesPoints = handle?.codeforces_handles.reduce((acc, handle) => {
    return acc + getPlatformPoints(handle, 'codeforces')
  }, 0) ?? 0
  const atcoderPoints = handle?.atcoder_handles.reduce((acc, handle) => {
    return acc + getPlatformPoints(handle, 'atcoder')
  }, 0) ?? 0
  return {
    codeforces: codeforcesPoints,
    atcoder: atcoderPoints,
    total: codeforcesPoints + atcoderPoints,
  }
}
