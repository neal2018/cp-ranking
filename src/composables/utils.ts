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
    return 0.5
  }
  if (platform === 'zealots') {
    return 0.1
  }
  return 0
}

export const getDivisionMultiplier = (division: number, platform: string) => {
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

export const getUpsolveMultiplier = (upsolved: boolean, platform: string) => {
  if (platform === 'codeforces' || platform === 'icpc') {
    return upsolved ? 0.5 : 1
  }
  if (platform === 'zealots') {
    return upsolved ? 0 : 1
  }
  return 1
}

export const getSolvedMultiplier = (solved: boolean, platform: string) => {
  if (platform === 'icpc')
    return solved ? 1 : 0.5
  return solved ? 1 : 0

}

export const getPointFromProblem = (upsolved: boolean, division: number, problem_id: string, platform: string) => {
  return getUpsolveMultiplier(upsolved, platform) * getDivisionMultiplier(division, platform) * getPartMultiplier(problem_id, platform) * getPointFromProblemId(problem_id, platform)
}

const getPlatformPoints = (handle: string, platform: string) => {
  return submissions.reduce((acc, submission) => {
    if (submission.handle.toLowerCase() === handle.toLowerCase()
      && submission.platform === platform && submission.solved)
      return acc + getPointFromProblem(submission.upsolved, submission.division, submission.problem_id, platform)
    return acc
  }, 0)
}

const getPlatformParticipation = (handle: string, platform: string) => {
  const contests = new Set<string>()
  if (platform === 'codeforces')
    return submissions.reduce((acc, submission) => {
      if (submission.handle.toLowerCase() === handle.toLowerCase()
        && submission.platform === platform && !submission.upsolved && !contests.has(submission.contest_id)) {
        contests.add(submission.contest_id)
        return acc + 0.5
      }
      return acc
    }, 0)
  if (platform === 'icpc') {
    const has_solved_solution = new Map<string, boolean>()
    submissions.forEach((submission) => {
      if (submission.handle.toLowerCase() === handle.toLowerCase())
        if (!has_solved_solution.has(submission.contest_id))
          has_solved_solution.set(submission.contest_id, submission.solved)
        else
          has_solved_solution.set(submission.contest_id, has_solved_solution.get(submission.contest_id) || submission.solved)
    })
    return submissions.reduce((acc, submission) => {
      if (submission.handle.toLowerCase() === handle.toLowerCase()
        && submission.platform === platform && !submission.upsolved && !contests.has(submission.contest_id)) {
        contests.add(submission.contest_id)
        return acc + submission.division * getSolvedMultiplier(has_solved_solution.get(submission.contest_id)!, submission.platform) * (acc >= 55 ? 1 : 5)
      }
      return acc
    }, 0)
    return 0
  }
  return 0
}

export const getPoints = (username: string) => {
  const handle = handles.find(handle => handle.username === username)
  const atcoderPoints = handle?.atcoder_handles.reduce((acc, handle) => {
    return acc + getPlatformPoints(handle, 'atcoder')
  }, 0) ?? 0
  const codeforcesPoints = handle?.codeforces_handles.reduce((acc, handle) => {
    return acc + getPlatformPoints(handle, 'codeforces')
  }, 0) ?? 0
  const codeforcesParticipation = handle?.codeforces_handles.reduce((acc, handle) => {
    return acc + getPlatformParticipation(handle, 'codeforces')
  }, 0) ?? 0
  const icpcPoints = handle?.codeforces_handles.reduce((acc, handle) => {
    return acc + getPlatformPoints(handle, 'icpc')
  }, 0) ?? 0
  const zealotsPoints = handle?.codeforces_handles.reduce((acc, handle) => {
    return acc + getPlatformPoints(handle, 'zealots')
  }, 0) ?? 0
  const icpcParticipation = handle?.codeforces_handles.reduce((acc, handle) => {
    return acc + getPlatformParticipation(handle, 'icpc')
  }, 0) ?? 0
  return {
    codeforces: codeforcesPoints,
    codeforcesParticipation: codeforcesParticipation,
    atcoder: atcoderPoints,
    icpc: icpcPoints,
    icpcParticipation: icpcParticipation,
    zealots: zealotsPoints.toFixed(1),
    total: codeforcesPoints + codeforcesParticipation + atcoderPoints + icpcPoints,
  }
}

export const getTableData = () => {
  const tableData = handles.map((handle) => {
    // TODO: improve time complexity
    const { codeforces, codeforcesParticipation, atcoder, icpc, icpcParticipation, zealots, total } = getPoints(handle.username)
    return {
      rank: 0,
      username: handle.username,
      codeforces,
      codeforcesParticipation,
      atcoder,
      icpc,
      icpcParticipation,
      zealots,
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
