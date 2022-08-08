import ApiService from '@/services/api.service'

class AttributeValueService {
  constructor() {
    this.request = ApiService
  }

  list(params = {}) {
    return this.request.get('/attribute-filters/', params)
  }

  update(id, payload) {
    return this.request.patch(`/attribute-filters/${id}/`, payload)
  }

  get(id) {
    return this.request.get(`/attribute-filters/${id}/`)
  }
}

export default new AttributeValueService()
