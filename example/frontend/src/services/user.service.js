import ApiService from '@/services/api.service'

class UserService {
  constructor() {
    this.request = ApiService
  }

  list(params = {}) {
    return this.request.get('/users/', params)
  }

  update(id, payload) {
    return this.request.patch(`/users/${id}/`, payload)
  }

  get(id) {
    return this.request.get(`/users/${id}/`)
  }
}

export default new UserService()
