import ApiService from '@/services/api.service'

class PossibleValueService {
  constructor() {
    this.request = ApiService
  }

  list(id, params = {}) {
    return this.request.get(`/possible-values/${id}/`, params)
  }

  update(id, payload) {
    return this.request.patch(`/possible-values/${id}/`, payload)
  }

  get(id) {
    return this.request.get(`/possible-values/${id}/`)
  }
}

export default new PossibleValueService()
