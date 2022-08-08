import ApiService from '@/services/api.service'

class ActionService {
  constructor() {
    this.request = ApiService
  }

  list(params = {}) {
    return this.request.get('/actions/', params)
  }

  update(id, payload) {
    return this.request.patch(`/actions/${id}/`, payload)
  }

  get(id) {
    return this.request.get(`/actions/${id}/`)
  }
}

export default new ActionService()
