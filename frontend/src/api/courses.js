import { apiRequest } from './client'

export function getCourses() {
  return apiRequest('/courses')
}

export function getCourse(courseId) {
  return apiRequest(`/courses/${courseId}`)
}
