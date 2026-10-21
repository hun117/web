import { apiRequest } from './client'

export function getPosts() {
  return apiRequest('/board/list')
}

export function getPost(postId) {
  return apiRequest(`/board/read/${postId}`)
}

export function createPost(post) {
  return apiRequest('/board/rergister', {
    method: 'POST',
    body: JSON.stringify(post),
  })
}
