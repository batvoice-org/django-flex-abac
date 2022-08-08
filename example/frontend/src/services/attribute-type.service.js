import ApiService from '@/services/api.service'

class AttributeTypeService {
  constructor() {
    this.request = ApiService
  }

  list(params = {}) {
    return this.request.get('/attribute-types/', params)
  }

  update(id, payload) {
    return this.request.patch(`/attribute-types/${id}/`, payload)
  }

  get(id) {
    return this.request.get(`/attribute-types/${id}/`)
  }
}

export default new AttributeTypeService()
