import ApiService from '@/services/api.service'

class PolicyService {
  constructor() {
    this.request = ApiService
  }

  list(params = {}) {
    return this.request.get('/policies/', params)
  }

  create(data) {
    return this.request.post('/policies/', data)
  }

  update(policiesId, payload) {
    return this.request.patch(`/policies/${policiesId}/`, payload)
  }

  get(policiesId) {
    return this.request.get(`/policies/${policiesId}/`)
  }
}

export default new PolicyService()
