import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useConfirmStore = defineStore('confirm', () => {
  const show = ref(false)
  const title = ref('Bist du sicher?')
  const message = ref('')
  const type = ref('warning') // 'warning', 'danger', 'info'
  const confirmText = ref('Ja, fortfahren')
  const cancelText = ref('Abbrechen')
  
  let resolvePromise = null

  function ask({ 
    title: t = 'Bist du sicher?', 
    message: msg = '', 
    type: tp = 'warning', 
    confirmText: ct = 'Ja, fortfahren', 
    cancelText: cl = 'Abbrechen' 
  }) {
    title.value = t
    message.value = msg
    type.value = tp
    confirmText.value = ct
    cancelText.value = cl
    show.value = true

    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  function confirm() {
    show.value = false
    if (resolvePromise) resolvePromise(true)
  }

  function cancel() {
    show.value = false
    if (resolvePromise) resolvePromise(false)
  }

  return {
    show,
    title,
    message,
    type,
    confirmText,
    cancelText,
    ask,
    confirm,
    cancel
  }
})
