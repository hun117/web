import { ref } from 'vue'
import { getCurrentUser } from '../api/auth'

export const currentUser = ref(null)

export function setCurrentUser(user) {
  currentUser.value = user
    ? {
        email: user.email || '',
        displayName: user.display_name || user.email || '',
        displayKind: user.display_kind || 'email',
      }
    : null
}

export async function restoreCurrentUser() {
  try {
    setCurrentUser(await getCurrentUser())
  } catch {
    setCurrentUser(null)
  }
}
