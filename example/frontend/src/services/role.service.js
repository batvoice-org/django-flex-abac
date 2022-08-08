import ApiService from '@/services/api.service'

class RoleService {
  constructor() {
    this.request = ApiService
  }

  list(params = {}) {
    return this.request.get('/roles/', params)
  }

  update(rolesId, payload) {
    return this.request.patch(`/roles/${rolesId}/`, payload)
  }

  create(data) {
    return this.request.post('/roles/', data)
  }

  deleteObject(rolesId) {
    return this.request.delete(`/roles/${rolesId}/`)
  }

  get(rolesId) {
    return this.request.get(`/roles/${rolesId}/`)
  }
}

export default new RoleService()

